<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { authStore } from '$lib/stores/auth';
	import { Avatar, Icon, Spinner } from '$lib/components/ui';

	type StoryItem = {
		id: string;
		media_type: string;
		caption?: string | null;
		is_single_view: boolean;
		viewed: boolean;
		media_url?: string | null;
		consumed?: boolean;
	};
	type Group = {
		creator_id: string;
		creator_username: string;
		creator_display_name: string;
		creator_avatar?: string | null;
		stories: StoryItem[];
		all_viewed: boolean;
	};

	let groups: Group[] = [];
	let loading = true;

	$: user = $authStore.user;
	$: isCreator = !!user?.is_creator;

	// Görüntüleyici durumu
	let viewerOpen = false;
	let activeGroup: Group | null = null;
	let idx = 0;
	let currentMedia: string | null = null;
	let currentConsumed = false;
	let viewerLoading = false;

	// Ekleme durumu
	let addOpen = false;
	let uploading = false;
	let addError = '';
	let form = { single_view: false, subscribers_only: false, caption: '' };
	let fileInput: HTMLInputElement;

	async function load() {
		loading = true;
		try {
			groups = await api.stories.feed();
		} catch {
			groups = [];
		} finally {
			loading = false;
		}
	}
	onMount(load);

	async function openGroup(g: Group) {
		activeGroup = g;
		idx = 0;
		viewerOpen = true;
		await showCurrent();
	}

	async function showCurrent() {
		if (!activeGroup) return;
		const s = activeGroup.stories[idx];
		if (!s) return closeViewer();
		viewerLoading = true;
		currentMedia = null;
		try {
			const res: any = await api.stories.view(s.id);
			currentMedia = res?.media_url ?? null;
			currentConsumed = !!res?.consumed;
			s.viewed = true;
		} catch (e) {
			currentMedia = null;
		} finally {
			viewerLoading = false;
		}
	}

	async function next() {
		if (!activeGroup) return;
		if (idx < activeGroup.stories.length - 1) {
			idx += 1;
			await showCurrent();
		} else {
			closeViewer();
		}
	}
	function prev() {
		if (idx > 0) {
			idx -= 1;
			showCurrent();
		}
	}
	function closeViewer() {
		viewerOpen = false;
		activeGroup = null;
		currentMedia = null;
	}

	async function onFile(e: Event) {
		const file = (e.target as HTMLInputElement).files?.[0];
		if (!file) return;
		uploading = true;
		addError = '';
		try {
			const up: any = await api.posts.uploadMedia(file);
			const url = up?.url ?? up?.media_url ?? up?.location;
			if (!url) throw new Error('Yükleme başarısız');
			const media_type = file.type.startsWith('video') ? 'video' : 'image';
			await api.stories.create({
				media_url: url,
				media_type,
				caption: form.caption || undefined,
				single_view: form.single_view,
				subscribers_only: form.subscribers_only
			});
			addOpen = false;
			form = { single_view: false, subscribers_only: false, caption: '' };
			await load();
		} catch (err: any) {
			addError = err?.message || 'Hikaye eklenemedi';
		} finally {
			uploading = false;
			if (fileInput) fileInput.value = '';
		}
	}
</script>

{#if loading}
	<div class="flex gap-3 overflow-hidden py-1">
		{#each Array(5) as _}<div class="w-16 h-16 rounded-full skeleton shrink-0"></div>{/each}
	</div>
{:else if groups.length > 0 || isCreator}
	<div class="flex gap-4 overflow-x-auto scrollbar-hide pb-2">
		{#if isCreator}
			<button class="flex flex-col items-center gap-1.5 shrink-0 w-16" on:click={() => (addOpen = true)}>
				<span class="relative grid place-items-center w-16 h-16 rounded-full bg-muted border-2 border-dashed border-border text-primary">
					<Icon name="plus" size={22} />
				</span>
				<span class="text-[11px] text-muted-foreground truncate w-full text-center">Ekle</span>
			</button>
		{/if}
		{#each groups as g}
			<button class="flex flex-col items-center gap-1.5 shrink-0 w-16" on:click={() => openGroup(g)}>
				<span class="rounded-full p-[2px] {g.all_viewed ? 'bg-border' : 'bg-gradient-to-tr from-primary to-primary-400'}">
					<span class="block rounded-full p-[2px] bg-background">
						<Avatar src={g.creator_avatar} alt={g.creator_display_name} size="lg" />
					</span>
				</span>
				<span class="text-[11px] text-muted-foreground truncate w-full text-center">{g.creator_username}</span>
			</button>
		{/each}
	</div>
{/if}

<!-- Ekleme modalı -->
{#if addOpen}
	<div class="fixed inset-0 z-50 grid place-items-center bg-black/60 p-4" on:click|self={() => (addOpen = false)} role="presentation">
		<div class="w-full max-w-sm rounded-2xl bg-card border border-border p-5 space-y-4">
			<div class="flex items-center justify-between">
				<h3 class="font-semibold">Hikaye ekle</h3>
				<button class="text-muted-foreground hover:text-foreground" on:click={() => (addOpen = false)}><Icon name="x" size={20} /></button>
			</div>
			<input bind:value={form.caption} class="input" placeholder="Açıklama (opsiyonel)" maxlength="500" />
			<label class="flex items-center gap-2 text-sm">
				<input type="checkbox" bind:checked={form.single_view} /> Tek görüntülük (şipşak — bir kez açılır)
			</label>
			<label class="flex items-center gap-2 text-sm">
				<input type="checkbox" bind:checked={form.subscribers_only} /> Sadece abonelere
			</label>
			{#if addError}<p class="text-sm text-destructive">{addError}</p>{/if}
			<input bind:this={fileInput} type="file" accept="image/*,video/*" class="hidden" on:change={onFile} />
			<button
				class="btn-primary w-full"
				disabled={uploading}
				on:click={() => fileInput?.click()}
			>
				{#if uploading}<Spinner />{:else}<Icon name="image" size={16} class="mr-1.5" />Medya seç & paylaş{/if}
			</button>
		</div>
	</div>
{/if}

<!-- Görüntüleyici -->
{#if viewerOpen && activeGroup}
	<div class="fixed inset-0 z-50 bg-black flex flex-col" role="presentation">
		<!-- İlerleme çubukları -->
		<div class="flex gap-1 p-3">
			{#each activeGroup.stories as _, i}
				<div class="h-1 flex-1 rounded-full {i <= idx ? 'bg-white' : 'bg-white/30'}"></div>
			{/each}
		</div>
		<div class="flex items-center gap-3 px-4 pb-2 text-white">
			<Avatar src={activeGroup.creator_avatar} alt={activeGroup.creator_display_name} size="sm" />
			<span class="font-medium text-sm">{activeGroup.creator_username}</span>
			{#if activeGroup.stories[idx]?.is_single_view}
				<span class="badge bg-primary/20 text-primary text-[10px]">tek görüntülük</span>
			{/if}
			<button class="ml-auto text-white/80 hover:text-white" on:click={closeViewer}><Icon name="x" size={24} /></button>
		</div>

		<div class="relative flex-1 grid place-items-center overflow-hidden">
			<!-- Dokunma alanları -->
			<button class="absolute inset-y-0 left-0 w-1/3 z-10" on:click={prev} aria-label="Önceki"></button>
			<button class="absolute inset-y-0 right-0 w-1/3 z-10" on:click={next} aria-label="Sonraki"></button>

			{#if viewerLoading}
				<Spinner />
			{:else if currentMedia}
				{#if activeGroup.stories[idx]?.media_type === 'video'}
					<video src={currentMedia} class="max-h-full max-w-full" autoplay controls playsinline></video>
				{:else}
					<img src={currentMedia} alt="" class="max-h-full max-w-full object-contain select-none" />
				{/if}
			{:else}
				<div class="text-center text-white/70 px-8">
					<Icon name="eye" size={40} class="mx-auto mb-3 opacity-60" />
					<p class="text-sm">Bu tek görüntülük hikaye zaten açıldı ve artık görüntülenemez.</p>
				</div>
			{/if}

			{#if activeGroup.stories[idx]?.caption && currentMedia}
				<div class="absolute bottom-6 inset-x-0 px-6 text-center text-white text-sm drop-shadow">
					{activeGroup.stories[idx].caption}
				</div>
			{/if}
		</div>
	</div>
{/if}
