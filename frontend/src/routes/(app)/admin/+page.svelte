<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { api, adminApi } from '$lib/api/client';
	import { authStore } from '$lib/stores/auth';
	import { waitForAuth, isStaff } from '$lib/utils/auth';
	import { Button, Input, Spinner, Icon } from '$lib/components/ui';
	import { formatCurrency } from '$lib/utils';

	type Tab = 'overview' | 'reports' | 'tickets' | 'withdrawals' | 'escrow' | 'ads' | 'credit' | 'users';
	let tab: Tab = 'overview';
	let ready = false;
	let loading = false;
	let error = '';
	let notice = '';

	let stats: any = null;
	let reports: any[] = [];
	let tickets: any[] = [];
	let withdrawals: any[] = [];
	let disputes: any[] = [];
	let ads: any[] = [];
	let users: any[] = [];

	// Bakiye formu
	let creditUser = '';
	let creditAmount = 0;
	let creditNote = '';
	let bulkAmount = 10000;
	let bulkSet = false;
	// Reklam formu
	let adForm = {
		title: '', ad_type: 'image', placement: 'feed', media_url: '', text_content: '',
		link_url: '', display_percent: 100, target_audience: 'all', skip_after: 3, is_active: true
	};
	// Kullanıcı arama
	let userSearch = '';

	const tabs: { id: Tab; label: string; icon: string }[] = [
		{ id: 'overview', label: 'Genel Bakış', icon: 'home' },
		{ id: 'reports', label: 'Şikayetler', icon: 'flag' },
		{ id: 'tickets', label: 'Destek', icon: 'headset' },
		{ id: 'withdrawals', label: 'Çekimler', icon: 'wallet' },
		{ id: 'escrow', label: 'Emanet', icon: 'shield' },
		{ id: 'ads', label: 'Reklamlar', icon: 'image' },
		{ id: 'credit', label: 'Bakiye', icon: 'dollar' },
		{ id: 'users', label: 'Kullanıcılar', icon: 'user' }
	];

	function flash(msg: string) {
		notice = msg;
		setTimeout(() => (notice = ''), 3000);
	}

	async function load(t: Tab) {
		loading = true;
		error = '';
		try {
			if (t === 'overview') stats = await adminApi.getStats();
			else if (t === 'reports') reports = await api.reports.queue('pending');
			else if (t === 'tickets') tickets = await api.tickets.queue();
			else if (t === 'withdrawals') withdrawals = await adminApi.listWithdrawals('pending');
			else if (t === 'escrow') disputes = await api.escrow.disputes();
			else if (t === 'ads') ads = await api.ads.all();
			else if (t === 'users') users = ((await adminApi.listUsers({ search: userSearch })) as any)?.items ?? [];
		} catch (e: any) {
			error = e?.message || 'Yüklenemedi';
		} finally {
			loading = false;
		}
	}

	function selectTab(t: Tab) {
		tab = t;
		load(t);
	}

	onMount(async () => {
		await waitForAuth();
		if (!isStaff($authStore.user)) {
			goto('/');
			return;
		}
		ready = true;
		load('overview');
	});

	async function resolveReport(id: string, action: string) {
		try {
			await api.reports.resolve(id, { status: 'resolved', action_taken: action });
			reports = reports.filter((r) => r.id !== id);
			flash('Şikayet çözümlendi');
		} catch (e: any) { error = e?.message; }
	}
	async function approveWd(id: string) {
		try { await adminApi.approveWithdrawal(id); withdrawals = withdrawals.filter((w) => w.id !== id); flash('Çekim onaylandı ve gönderildi'); }
		catch (e: any) { error = e?.message; }
	}
	async function rejectWd(id: string) {
		const reason = prompt('Red gerekçesi:') || 'Reddedildi';
		try { await adminApi.rejectWithdrawal(id, reason); withdrawals = withdrawals.filter((w) => w.id !== id); flash('Çekim reddedildi, bakiye iade edildi'); }
		catch (e: any) { error = e?.message; }
	}
	async function resolveEscrow(id: string, action: 'release' | 'refund') {
		try { await api.escrow.resolve(id, action); disputes = disputes.filter((d) => d.id !== id); flash(action === 'release' ? 'Üreticiye ödendi' : 'Alıcıya iade edildi'); }
		catch (e: any) { error = e?.message; }
	}
	async function doCredit() {
		if (!creditUser || creditAmount <= 0) { error = 'Kullanıcı ve tutar gerekli'; return; }
		try { const r: any = await adminApi.credit(creditUser, creditAmount, creditNote); flash(`${creditUser} → yeni bakiye: ${formatCurrency(r.balance)}`); creditAmount = 0; creditNote = ''; }
		catch (e: any) { error = e?.message; }
	}
	async function doCreditAll() {
		if (!confirm(`TÜM kullanıcılara ${bulkSet ? 'bakiye = ' : '+'}${formatCurrency(bulkAmount)} uygulansın mı?`)) return;
		try { const r: any = await adminApi.creditAll(bulkAmount, { set: bulkSet }); flash(`${r.updated_users} kullanıcı güncellendi`); }
		catch (e: any) { error = e?.message; }
	}
	async function setUserBalance(u: any) {
		const v = prompt(`@${u.username} için yeni bakiye (TL):`, String(u.balance ?? 0));
		if (v === null) return;
		const bal = parseFloat(v);
		if (isNaN(bal) || bal < 0) { error = 'Geçersiz bakiye'; return; }
		try { const r: any = await adminApi.setBalance(u.id, bal); u.balance = r.balance; users = users; flash(`@${u.username} → ${formatCurrency(r.balance)}`); }
		catch (e: any) { error = e?.message; }
	}
	async function createAd() {
		if (!adForm.title) { error = 'Başlık gerekli'; return; }
		if (adForm.ad_type !== 'text' && !adForm.media_url) { error = 'Görsel/video adresi gerekli'; return; }
		try {
			await api.ads.create({ ...adForm, display_percent: Number(adForm.display_percent) || 100, skip_after: Number(adForm.skip_after) || 3 });
			adForm = { title: '', ad_type: 'image', placement: 'feed', media_url: '', text_content: '', link_url: '', display_percent: 100, target_audience: 'all', skip_after: 3, is_active: true };
			ads = await api.ads.all();
			flash('Reklam eklendi');
		} catch (e: any) { error = e?.message; }
	}
	async function removeAd(id: string) {
		try { await api.ads.remove(id); ads = ads.filter((a) => a.id !== id); flash('Reklam silindi'); }
		catch (e: any) { error = e?.message; }
	}
	async function setRole(u: any, role: string) {
		try { await adminApi.setRole(u.id, role); u.role = role; users = users; flash(`@${u.username} → ${role}`); }
		catch (e: any) { error = e?.message; }
	}
	async function toggleBan(u: any) {
		try {
			if (u.status === 'banned' || u.is_banned) { await adminApi.unbanUser(u.id); u.status = 'active'; u.is_banned = false; flash('Yasak kaldırıldı'); }
			else { const reason = prompt('Yasaklama gerekçesi:') || 'Kural ihlali'; await adminApi.banUser(u.id, reason); u.status = 'banned'; u.is_banned = true; flash('Kullanıcı yasaklandı'); }
			users = users;
		} catch (e: any) { error = e?.message; }
	}
</script>

<svelte:head><title>Yönetim Paneli — Sadece Fanlar</title></svelte:head>

{#if !ready}
	<div class="flex justify-center py-20"><Spinner /></div>
{:else}
	<div class="space-y-5">
		<div class="flex items-center gap-2">
			<Icon name="shield" size={22} class="text-primary" />
			<h1 class="text-xl font-semibold">Yönetim Paneli</h1>
		</div>

		<!-- Sekme barı -->
		<div class="flex gap-1 overflow-x-auto scrollbar-hide border-b border-border pb-px">
			{#each tabs as t}
				<button
					class="flex items-center gap-2 px-3 py-2 text-sm rounded-t-lg whitespace-nowrap transition-colors {tab === t.id ? 'text-primary border-b-2 border-primary font-medium' : 'text-muted-foreground hover:text-foreground'}"
					on:click={() => selectTab(t.id)}
				>
					<Icon name={t.icon} size={16} />{t.label}
				</button>
			{/each}
		</div>

		{#if notice}<div class="rounded-lg bg-primary/10 text-primary text-sm px-4 py-2">{notice}</div>{/if}
		{#if error}<div class="rounded-lg bg-destructive/10 text-destructive text-sm px-4 py-2">{error}</div>{/if}

		{#if loading}
			<div class="flex justify-center py-12"><Spinner /></div>
		{:else}
			{#if tab === 'overview'}
				{#if stats}
					<div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
						{#each [
							{ label: 'Toplam kullanıcı', value: stats.total_users },
							{ label: 'İçerik üreticisi', value: stats.total_creators },
							{ label: 'Toplam gönderi', value: stats.total_posts },
							{ label: 'Aktif abonelik', value: stats.active_subscriptions },
							{ label: 'Bekleyen şikayet', value: stats.pending_reports },
							{ label: 'Bekleyen çekim', value: stats.pending_withdrawals }
						] as s}
							<div class="rounded-xl border border-border bg-card p-4">
								<p class="text-2xl font-semibold">{s.value ?? 0}</p>
								<p class="text-xs text-muted-foreground mt-1">{s.label}</p>
							</div>
						{/each}
						<div class="rounded-xl border border-border bg-card p-4">
							<p class="text-2xl font-semibold">{formatCurrency(stats.total_revenue ?? 0)}</p>
							<p class="text-xs text-muted-foreground mt-1">Platform geliri (komisyon)</p>
						</div>
						<div class="rounded-xl border border-border bg-card p-4">
							<p class="text-2xl font-semibold">{formatCurrency(stats.pending_withdrawal_amount ?? 0)}</p>
							<p class="text-xs text-muted-foreground mt-1">Bekleyen çekim tutarı</p>
						</div>
					</div>
				{/if}

			{:else if tab === 'reports'}
				{#if reports.length === 0}<p class="text-sm text-muted-foreground py-8 text-center">Bekleyen şikayet yok.</p>{/if}
				<div class="space-y-3">
					{#each reports as r}
						<div class="rounded-xl border border-border bg-card p-4">
							<div class="flex items-start justify-between gap-3">
								<div class="min-w-0">
									<span class="badge badge-warning mb-1">{r.type ?? r.reported_type}</span>
									<p class="text-sm">{r.description || 'Açıklama yok'}</p>
									<p class="text-xs text-muted-foreground mt-1">Hedef: {r.reported_type} · {r.reported_id}</p>
								</div>
								<div class="flex gap-2 shrink-0">
									<Button size="sm" variant="outline" on:click={() => resolveReport(r.id, 'dismiss')}>Reddet</Button>
									<Button size="sm" variant="danger" on:click={() => resolveReport(r.id, 'content_removed')}>İçeriği kaldır</Button>
								</div>
							</div>
						</div>
					{/each}
				</div>

			{:else if tab === 'tickets'}
				{#if tickets.length === 0}<p class="text-sm text-muted-foreground py-8 text-center">Bekleyen destek talebi yok.</p>{/if}
				<div class="space-y-3">
					{#each tickets as t}
						<a href="/support?ticket={t.id}" class="block rounded-xl border border-border bg-card p-4 hover:border-primary/50 transition-colors">
							<div class="flex items-center justify-between gap-3">
								<div class="min-w-0">
									<p class="font-medium text-sm truncate">{t.subject}</p>
									<p class="text-xs text-muted-foreground mt-0.5">{t.category || 'genel'} · {t.status}</p>
								</div>
								<Icon name="message" size={18} class="text-muted-foreground shrink-0" />
							</div>
						</a>
					{/each}
				</div>

			{:else if tab === 'withdrawals'}
				{#if withdrawals.length === 0}<p class="text-sm text-muted-foreground py-8 text-center">Bekleyen çekim talebi yok.</p>{/if}
				<div class="space-y-3">
					{#each withdrawals as w}
						<div class="rounded-xl border border-border bg-card p-4">
							<div class="flex items-start justify-between gap-3">
								<div class="min-w-0">
									<p class="font-medium">{formatCurrency(w.amount)} <span class="text-xs text-muted-foreground">net {formatCurrency(w.net_amount)} · {w.payment_method}</span></p>
									<p class="text-xs text-muted-foreground mt-1 font-mono break-all">{w.payout_address}</p>
									{#if w.crypto_amount}<p class="text-xs text-muted-foreground">≈ {w.crypto_amount} kripto</p>{/if}
								</div>
								<div class="flex gap-2 shrink-0">
									<Button size="sm" variant="outline" on:click={() => rejectWd(w.id)}>Reddet</Button>
									<Button size="sm" on:click={() => approveWd(w.id)}>Onayla & Gönder</Button>
								</div>
							</div>
						</div>
					{/each}
				</div>

			{:else if tab === 'escrow'}
				{#if disputes.length === 0}<p class="text-sm text-muted-foreground py-8 text-center">Anlaşmazlık yok.</p>{/if}
				<div class="space-y-3">
					{#each disputes as d}
						<div class="rounded-xl border border-border bg-card p-4">
							<p class="font-medium text-sm">{d.title} — {formatCurrency(d.amount)}</p>
							<p class="text-sm text-muted-foreground mt-1">{d.description}</p>
							{#if d.dispute_reason}<p class="text-xs text-destructive mt-1">Anlaşmazlık: {d.dispute_reason}</p>{/if}
							<div class="flex gap-2 mt-3">
								<Button size="sm" variant="outline" on:click={() => resolveEscrow(d.id, 'refund')}>Alıcıya iade</Button>
								<Button size="sm" on:click={() => resolveEscrow(d.id, 'release')}>Üreticiye öde</Button>
							</div>
						</div>
					{/each}
				</div>

			{:else if tab === 'ads'}
				<div class="rounded-xl border border-border bg-card p-4 space-y-3">
					<p class="font-medium text-sm">Yeni reklam (özel — Google Ads değil)</p>
					<Input bind:value={adForm.title} placeholder="Başlık" />
					<div class="grid grid-cols-2 gap-2 text-sm">
						<label class="flex flex-col gap-1">Tür
							<select bind:value={adForm.ad_type} class="input h-9">
								<option value="image">Resim</option>
								<option value="video">Video</option>
								<option value="text">Metin</option>
							</select>
						</label>
						<label class="flex flex-col gap-1">Yerleşim
							<select bind:value={adForm.placement} class="input h-9">
								<option value="feed">Akış</option>
								<option value="explore">Keşfet üst</option>
								<option value="explore_left">Keşfet sol</option>
								<option value="explore_right">Keşfet sağ</option>
								<option value="sidebar">Kenar çubuğu</option>
								<option value="preroll">Video öncesi (pre-roll)</option>
							</select>
						</label>
					</div>
					{#if adForm.ad_type !== 'text'}
						<Input bind:value={adForm.media_url} placeholder={adForm.ad_type === 'video' ? 'Video URL (mp4/webm)' : 'Görsel URL'} />
					{/if}
					{#if adForm.ad_type === 'text'}
						<Input bind:value={adForm.text_content} placeholder="Metin içeriği" />
					{/if}
					<Input bind:value={adForm.link_url} placeholder="Hedef bağlantı (tıklanınca, opsiyonel)" />
					<div class="grid grid-cols-2 gap-2 text-sm">
						<label class="flex flex-col gap-1">Gösterim oranı (%)
							<Input type="number" bind:value={adForm.display_percent} placeholder="100" />
						</label>
						<label class="flex flex-col gap-1">Kitle
							<select bind:value={adForm.target_audience} class="input h-9">
								<option value="all">Herkes</option>
								<option value="guests">Misafirler</option>
								<option value="subscribers">Üyeler</option>
								<option value="creators">Üreticiler</option>
							</select>
						</label>
					</div>
					{#if adForm.placement === 'preroll'}
						<label class="flex flex-col gap-1 text-sm">Kaç saniye sonra atlanabilir
							<Input type="number" bind:value={adForm.skip_after} placeholder="3" />
						</label>
					{/if}
					<Button size="sm" on:click={createAd}>Ekle</Button>
				</div>
				<div class="space-y-3 mt-3">
					{#each ads as a}
						<div class="rounded-xl border border-border bg-card p-4 flex items-center justify-between gap-3">
							<div class="min-w-0">
								<p class="font-medium text-sm truncate">{a.title} <span class="text-xs text-muted-foreground">[{a.ad_type}]</span></p>
								<p class="text-xs text-muted-foreground">{a.placement} · %{a.display_percent} · {a.target_audience} · {a.is_active ? 'aktif' : 'pasif'} · {a.impressions ?? 0} gösterim · {a.clicks ?? 0} tık</p>
							</div>
							<Button size="sm" variant="danger" on:click={() => removeAd(a.id)}>Sil</Button>
						</div>
					{/each}
				</div>

			{:else if tab === 'credit'}
				<div class="grid sm:grid-cols-2 gap-3">
					<div class="rounded-xl border border-border bg-card p-4 space-y-3">
						<p class="font-medium text-sm">Tek kullanıcıya bakiye ekle (TL)</p>
						<Input bind:value={creditUser} placeholder="Kullanıcı adı" />
						<Input type="number" bind:value={creditAmount} placeholder="Tutar (TL)" />
						<Input bind:value={creditNote} placeholder="Not (opsiyonel)" />
						<Button size="sm" on:click={doCredit}>Bakiye ekle</Button>
					</div>
					<div class="rounded-xl border border-border bg-card p-4 space-y-3">
						<p class="font-medium text-sm">Toplu işlem (tüm kullanıcılar)</p>
						<Input type="number" bind:value={bulkAmount} placeholder="Tutar (TL)" />
						<label class="flex items-center gap-2 text-sm">
							<input type="checkbox" bind:checked={bulkSet} />
							Ekleme yerine bakiyeyi bu değere AYARLA
						</label>
						<Button size="sm" variant="outline" on:click={doCreditAll}>Tüm kullanıcılara uygula</Button>
						<p class="text-xs text-muted-foreground">Not: Kullanıcı bazında bakiyeyi "Kullanıcılar" sekmesinden de ayarlayabilirsiniz.</p>
					</div>
				</div>

			{:else if tab === 'users'}
				<div class="flex gap-2 max-w-md">
					<Input bind:value={userSearch} placeholder="Kullanıcı ara…" on:keydown={(e) => e.key === 'Enter' && load('users')} />
					<Button size="sm" on:click={() => load('users')}>Ara</Button>
				</div>
				<div class="space-y-2 mt-3">
					{#each users as u}
						<div class="rounded-xl border border-border bg-card p-3 flex items-center justify-between gap-3">
							<div class="min-w-0">
								<p class="text-sm font-medium truncate">{u.display_name || u.username} <span class="text-xs text-muted-foreground">@{u.username}</span></p>
								<p class="text-xs text-muted-foreground">{u.role || 'user'} · {u.status || (u.is_banned ? 'banned' : 'active')}{#if u.balance != null} · {formatCurrency(u.balance)}{/if}</p>
							</div>
							<div class="flex flex-wrap gap-2 shrink-0 justify-end">
								<select class="input h-9 w-auto text-xs" on:change={(e) => setRole(u, e.currentTarget.value)}>
									<option value="user" selected={u.role === 'user' || !u.role}>user</option>
									<option value="moderator" selected={u.role === 'moderator'}>moderator</option>
									<option value="admin" selected={u.role === 'admin'}>admin</option>
								</select>
								<Button size="sm" variant="outline" on:click={() => setUserBalance(u)}>Bakiye</Button>
								<Button size="sm" variant={u.status === 'banned' || u.is_banned ? 'outline' : 'danger'} on:click={() => toggleBan(u)}>
									{u.status === 'banned' || u.is_banned ? 'Yasağı kaldır' : 'Yasakla'}
								</Button>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		{/if}
	</div>
{/if}
