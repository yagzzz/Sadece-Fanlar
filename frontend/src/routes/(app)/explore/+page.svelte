<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { UserCard, AdSlot, PostCard } from '$lib/components/features';
	import { Button, Input, Spinner, Skeleton, Icon } from '$lib/components/ui';
	import { debounce } from '$lib/utils';
	import type { User, Post } from '$lib/types';

	// Üst seviye: İçerikler mi Üreticiler mi
	let mainTab: 'content' | 'creators' = 'content';

	// İçerik keşfi
	let posts: Post[] = [];
	let postsLoading = true;
	let postsLoaded = false;

	// Üretici keşfi
	let users: User[] = [];
	let usersLoading = false;
	let usersLoaded = false;
	let searchQuery = '';
	let creatorSort = 'featured';

	const creatorSorts = [
		{ id: 'featured', label: 'Öne Çıkanlar' },
		{ id: 'new', label: 'Yeni' },
		{ id: 'popular', label: 'Popüler' }
	];

	async function loadPosts() {
		postsLoading = true;
		try {
			const res = await api.posts.getDiscover(1, 24);
			posts = res.items;
		} catch (e) {
			posts = [];
		} finally {
			postsLoading = false;
			postsLoaded = true;
		}
	}

	async function loadUsers() {
		usersLoading = true;
		try {
			const res = await api.users.explore({ sort: creatorSort, search: searchQuery || undefined, page: 1, limit: 24 });
			users = res.items;
		} catch (e) {
			users = [];
		} finally {
			usersLoading = false;
			usersLoaded = true;
		}
	}

	function switchTab(t: 'content' | 'creators') {
		mainTab = t;
		if (t === 'content' && !postsLoaded) loadPosts();
		if (t === 'creators' && !usersLoaded) loadUsers();
	}

	const debouncedSearch = debounce(() => loadUsers(), 300);

	async function handleLike(e: CustomEvent<string>) {
		try { await api.posts.like(e.detail); } catch {}
	}
	async function handleTip(e: CustomEvent<any>) {
		const post = e.detail;
		const rid = post?.author?.id ?? post?.user?.id;
		if (!rid) return;
		const v = prompt('Bahşiş tutarı (TL):', '10');
		if (!v) return;
		const amount = parseFloat(v);
		if (!amount || amount <= 0) return;
		try { await api.payments.tip(rid, amount, { postId: post.id }); alert('Bahşiş gönderildi!'); }
		catch (err: any) { alert(err?.message || 'Bahşiş başarısız'); }
	}
	async function handleUnlock(e: CustomEvent<any>) {
		const post = e.detail;
		if (!post?.id) return;
		if (!confirm(`İçeriğin kilidini ${post.ppv_price ?? ''} TL ile açmak ister misiniz?`)) return;
		try { await api.payments.unlockPost(post.id); posts = posts.map((p) => (p.id === post.id ? { ...p, is_unlocked: true } : p)); }
		catch (err: any) { alert(err?.message || 'Kilit açma başarısız'); }
	}

	onMount(loadPosts);
</script>

<svelte:head><title>Keşfet | SadeceFanlar</title></svelte:head>

<!-- Keşfet kenar reklamları -->
<div class="hidden 2xl:block fixed left-4 top-24 w-40 z-30"><AdSlot position="explore_left" vertical /></div>
<div class="hidden 2xl:block fixed right-4 top-24 w-40 z-30"><AdSlot position="explore_right" vertical /></div>

<div class="space-y-5">
	<h1 class="text-xl font-semibold">Keşfet</h1>

	<!-- Ana sekmeler: İçerikler / Üreticiler -->
	<div class="flex gap-1 border-b border-border">
		<button
			class="flex items-center gap-2 px-4 py-2.5 text-sm border-b-2 transition-colors {mainTab === 'content' ? 'border-primary text-primary font-medium' : 'border-transparent text-muted-foreground hover:text-foreground'}"
			on:click={() => switchTab('content')}
		>
			<Icon name="image" size={16} /> İçerikler
		</button>
		<button
			class="flex items-center gap-2 px-4 py-2.5 text-sm border-b-2 transition-colors {mainTab === 'creators' ? 'border-primary text-primary font-medium' : 'border-transparent text-muted-foreground hover:text-foreground'}"
			on:click={() => switchTab('creators')}
		>
			<Icon name="user" size={16} /> Üreticiler
		</button>
	</div>

	<AdSlot position="explore" />

	{#if mainTab === 'content'}
		{#if postsLoading}
			<div class="grid sm:grid-cols-2 gap-4">
				{#each Array(4) as _}
					<div class="rounded-xl border border-border bg-card p-4 space-y-3">
						<div class="flex items-center gap-3"><Skeleton variant="circular" width="40px" height="40px" /><Skeleton width="120px" /></div>
						<Skeleton variant="rectangular" height="200px" />
					</div>
				{/each}
			</div>
		{:else if posts.length === 0}
			<div class="text-center py-16">
				<div class="grid place-items-center w-14 h-14 rounded-2xl bg-muted text-muted-foreground mx-auto mb-4"><Icon name="image" size={28} /></div>
				<p class="font-medium mb-1">Henüz keşfedilecek içerik yok</p>
				<p class="text-sm text-muted-foreground">İçerik üreticileri paylaştıkça burada görünecek.</p>
			</div>
		{:else}
			<div class="grid sm:grid-cols-2 gap-4 items-start">
				{#each posts as post (post.id)}
					<PostCard {post} on:like={handleLike} on:tip={handleTip} on:unlock={handleUnlock} on:comment={(e) => (window.location.href = `/post/${e.detail}`)} />
				{/each}
			</div>
		{/if}
	{:else}
		<Input type="search" placeholder="İçerik üreticisi ara..." bind:value={searchQuery} on:input={() => debouncedSearch()} />
		<div class="flex gap-2">
			{#each creatorSorts as s}
				<button
					class="px-3 py-1.5 text-xs rounded-full border transition-colors {creatorSort === s.id ? 'border-primary text-primary bg-primary/5' : 'border-border text-muted-foreground hover:text-foreground'}"
					on:click={() => { creatorSort = s.id; loadUsers(); }}
				>{s.label}</button>
			{/each}
		</div>

		{#if usersLoading}
			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				{#each Array(6) as _}
					<div class="rounded-xl border border-border bg-card overflow-hidden">
						<Skeleton variant="rectangular" height="96px" />
						<div class="p-4 pt-10"><Skeleton width="60%" /><Skeleton lines={2} class="mt-3" /></div>
					</div>
				{/each}
			</div>
		{:else if users.length === 0}
			<div class="text-center py-16">
				<div class="grid place-items-center w-14 h-14 rounded-2xl bg-muted text-muted-foreground mx-auto mb-4"><Icon name="user" size={28} /></div>
				<p class="font-medium mb-1">İçerik üreticisi bulunamadı</p>
				<p class="text-sm text-muted-foreground">{searchQuery ? 'Farklı bir arama deneyin.' : 'Henüz üretici yok.'}</p>
			</div>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				{#each users as user (user.id)}
					<UserCard {user} on:subscribe={(e) => (window.location.href = `/${e.detail.username}`)} on:message={(e) => (window.location.href = `/messages/${e.detail.id}`)} />
				{/each}
			</div>
		{/if}
	{/if}
</div>
