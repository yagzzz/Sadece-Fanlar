<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';
	import { api } from '$lib/api';
	import { Button, Input, Spinner, Icon } from '$lib/components/ui';

	const dispatch = createEventDispatcher();

	let loading = true;
	let error = '';
	let verifying = false;
	let secret = '';
	let qrCode = '';
	let backupCodes: string[] = [];
	let code = '';

	onMount(async () => {
		try {
			const res: any = await api.auth.setup2FA();
			secret = res?.secret || '';
			qrCode = res?.qr_code || '';
			backupCodes = res?.backup_codes || [];
		} catch (e: any) {
			error = e?.message || '2FA kurulumu başlatılamadı';
		} finally {
			loading = false;
		}
	});

	async function verify() {
		if (code.length < 6) { error = '6 haneli kodu girin'; return; }
		verifying = true;
		error = '';
		try {
			await api.auth.verify2FA(code.trim());
			dispatch('enabled');
		} catch (e: any) {
			error = e?.message || 'Kod doğrulanamadı';
		} finally {
			verifying = false;
		}
	}

	function qrSrc(q: string): string {
		if (!q) return '';
		return q.startsWith('data:') ? q : `data:image/png;base64,${q}`;
	}
</script>

<div class="fixed inset-0 z-50 grid place-items-center bg-black/60 p-4" on:click|self={() => dispatch('close')} role="presentation">
	<div class="w-full max-w-md rounded-2xl bg-card border border-border p-5 space-y-4 max-h-[90vh] overflow-y-auto">
		<div class="flex items-center justify-between">
			<h3 class="font-semibold flex items-center gap-2"><Icon name="shield" size={18} class="text-primary" /> İki faktörlü doğrulama</h3>
			<button class="text-muted-foreground hover:text-foreground" on:click={() => dispatch('close')}><Icon name="x" size={20} /></button>
		</div>

		{#if loading}
			<div class="flex justify-center py-10"><Spinner /></div>
		{:else if error && !secret}
			<p class="text-sm text-destructive">{error}</p>
		{:else}
			<p class="text-sm text-muted-foreground">
				Authenticator uygulamanızla (Google Authenticator, Authy vb.) QR kodu tarayın veya anahtarı elle girin.
			</p>

			{#if qrCode}
				<div class="grid place-items-center">
					<img src={qrSrc(qrCode)} alt="2FA QR" class="w-44 h-44 rounded-lg bg-white p-2" />
				</div>
			{/if}

			<div>
				<p class="text-xs text-muted-foreground mb-1">Gizli anahtar</p>
				<code class="block text-xs bg-muted rounded-lg p-2 break-all select-all font-mono">{secret}</code>
			</div>

			{#if backupCodes.length}
				<div>
					<p class="text-xs text-muted-foreground mb-1">Yedek kodlar (güvenli yerde saklayın)</p>
					<div class="grid grid-cols-2 gap-1 text-xs font-mono bg-muted rounded-lg p-2">
						{#each backupCodes as bc}<span class="select-all">{bc}</span>{/each}
					</div>
				</div>
			{/if}

			<div>
				<p class="text-xs text-muted-foreground mb-1">Uygulamadaki 6 haneli kod</p>
				<Input bind:value={code} placeholder="000000" maxlength="6" />
			</div>
			{#if error}<p class="text-sm text-destructive">{error}</p>{/if}
			<Button class="w-full" disabled={verifying} on:click={verify}>
				{verifying ? 'Doğrulanıyor...' : 'Etkinleştir'}
			</Button>
		{/if}
	</div>
</div>
