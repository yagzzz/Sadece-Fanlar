<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { Modal, Button } from '$lib/components/ui';
	import { api } from '$lib/api';

	export let open = false;
	export let reportedType: 'post' | 'user' | 'message' | 'comment' = 'post';
	export let reportedId: string;
	export let reportedUserId: string | undefined = undefined;

	const dispatch = createEventDispatcher();

	const reasons = [
		{ id: 'ai_content', label: 'Yapay zeka üretimi içerik' },
		{ id: 'fake_content', label: 'Sahte / çalıntı içerik' },
		{ id: 'illegal_content', label: 'Yasa dışı içerik' },
		{ id: 'underage', label: 'Reşit olmayan / 18 yaş altı' },
		{ id: 'harassment', label: 'Taciz / hakaret' },
		{ id: 'impersonation', label: 'Kimlik taklidi' },
		{ id: 'spam', label: 'Spam' },
		{ id: 'other', label: 'Diğer' },
	];

	let selected = 'ai_content';
	let description = '';
	let sending = false;

	async function submit() {
		sending = true;
		try {
			await (api as any).reports.create({
				reported_type: reportedType,
				reported_id: reportedId,
				reported_user_id: reportedUserId,
				type: selected,
				description,
			});
			open = false;
			description = '';
			dispatch('done');
			alert('Şikayetiniz alındı. Ekibimiz inceleyecek.');
		} catch (e: any) {
			alert(e?.message || 'Şikayet gönderilemedi');
		} finally {
			sending = false;
		}
	}
</script>

<Modal {open} on:close={() => (open = false)} title="Şikayet Et">
	<div class="space-y-4">
		<p class="text-sm text-neutral-500">Şikayet nedeni seçin. Yapay zeka/sahte içerik dahil tüm ihlaller moderatörlere iletilir.</p>
		<div class="space-y-2">
			{#each reasons as r}
				<label class="flex items-center gap-2 text-sm cursor-pointer">
					<input type="radio" bind:group={selected} value={r.id} />
					<span>{r.label}</span>
				</label>
			{/each}
		</div>
		<textarea
			class="w-full rounded-lg border border-neutral-300 dark:border-neutral-700 bg-transparent px-3 py-2 text-sm"
			rows="3"
			placeholder="Ek açıklama (isteğe bağlı)"
			bind:value={description}
		></textarea>
		<div class="flex justify-end gap-2">
			<Button variant="outline" on:click={() => (open = false)}>Vazgeç</Button>
			<Button on:click={submit} disabled={sending}>Şikayeti Gönder</Button>
		</div>
	</div>
</Modal>
