<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth';
	import { waitForAuth } from '$lib/utils/auth';
	import { api } from '$lib/api';
	import { Button, Card, Input, Spinner } from '$lib/components/ui';
	import { timeAgo } from '$lib/utils';

	let tickets: any[] = [];
	let active: any = null;
	let loading = true;
	let creating = false;
	let subject = '';
	let firstMessage = '';
	let reply = '';
	let showNew = false;
	let pollTimer: any = null;

	async function load() {
		loading = true;
		tickets = await (api as any).tickets.mine();
		loading = false;
	}

	async function openTicket(id: string) {
		active = await (api as any).tickets.get(id);
		clearInterval(pollTimer);
		pollTimer = setInterval(async () => {
			if (active) active = await (api as any).tickets.get(active.id);
		}, 5000);
	}

	async function createTicket() {
		if (!subject.trim() || !firstMessage.trim()) return;
		creating = true;
		try {
			const t = await (api as any).tickets.create({ subject, message: firstMessage });
			subject = '';
			firstMessage = '';
			showNew = false;
			await load();
			await openTicket(t.id);
		} catch (e: any) {
			alert(e?.message || 'Talep oluşturulamadı');
		} finally {
			creating = false;
		}
	}

	async function sendReply() {
		if (!reply.trim() || !active) return;
		const text = reply;
		reply = '';
		await (api as any).tickets.reply(active.id, text);
		active = await (api as any).tickets.get(active.id);
	}

	onMount(async () => {
		await waitForAuth();
		if (!$authStore.user) { goto('/login'); return; }
		await load();
		return () => clearInterval(pollTimer);
	});
</script>

<svelte:head><title>Destek | SadeceFanlar</title></svelte:head>

<div>
	<div class="flex items-center justify-between mb-6">
		<h1 class="text-xl font-semibold">Destek</h1>
		<Button size="sm" on:click={() => (showNew = !showNew)}>Yeni Talep</Button>
	</div>

	{#if showNew}
		<Card class="p-4 mb-6 space-y-3">
			<Input label="Konu" bind:value={subject} placeholder="Sorununuzun konusu" />
			<textarea class="w-full rounded-lg border border-neutral-300 dark:border-neutral-700 bg-transparent px-3 py-2 text-sm" rows="3" placeholder="Mesajınız" bind:value={firstMessage}></textarea>
			<Button on:click={createTicket} disabled={creating}>Gönder</Button>
		</Card>
	{/if}

	{#if active}
		<Card class="p-4">
			<button class="text-sm text-neutral-500 mb-3" on:click={() => { active = null; clearInterval(pollTimer); }}>← Taleplerime dön</button>
			<h2 class="font-semibold mb-1">{active.subject}</h2>
			<p class="text-xs text-neutral-500 mb-4">Durum: {active.status === 'answered' ? 'Yanıtlandı (canlı sohbet)' : active.status === 'closed' ? 'Kapalı' : 'Açık'}</p>
			<div class="space-y-3 max-h-96 overflow-y-auto mb-4">
				{#each active.messages || [] as m}
					<div class="flex {m.is_staff ? 'justify-start' : 'justify-end'}">
						<div class="max-w-[75%] rounded-lg px-3 py-2 text-sm {m.is_staff ? 'bg-blue-100 dark:bg-blue-900/40' : 'bg-neutral-100 dark:bg-neutral-800'}">
							<p class="text-[10px] text-neutral-500 mb-0.5">{m.is_staff ? 'Destek Ekibi' : 'Siz'} · {timeAgo(m.created_at)}</p>
							<p class="whitespace-pre-wrap">{m.text}</p>
						</div>
					</div>
				{/each}
			</div>
			{#if active.status !== 'closed'}
				<div class="flex gap-2">
					<input class="flex-1 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-transparent px-3 py-2 text-sm" placeholder="Mesaj yaz..." bind:value={reply} on:keydown={(e) => e.key === 'Enter' && sendReply()} />
					<Button size="sm" on:click={sendReply}>Gönder</Button>
				</div>
			{/if}
		</Card>
	{:else if loading}
		<div class="flex justify-center py-12"><Spinner size="lg" /></div>
	{:else if tickets.length === 0}
		<p class="text-neutral-500 text-center py-12">Henüz destek talebiniz yok.</p>
	{:else}
		<div class="space-y-2">
			{#each tickets as t}
				<button class="w-full text-left p-4 rounded-lg border border-neutral-200 dark:border-neutral-800 hover:bg-neutral-50 dark:hover:bg-neutral-900" on:click={() => openTicket(t.id)}>
					<div class="flex justify-between">
						<span class="font-medium">{t.subject}</span>
						<span class="text-xs text-neutral-500">{t.status}</span>
					</div>
					<p class="text-xs text-neutral-500">{timeAgo(t.last_message_at)}</p>
				</button>
			{/each}
		</div>
	{/if}
</div>
