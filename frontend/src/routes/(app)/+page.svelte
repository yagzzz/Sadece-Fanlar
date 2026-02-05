<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { authStore } from '$lib/stores/auth';
	import { PostCard } from '$lib/components/features';
	import { Button, Spinner, Skeleton } from '$lib/components/ui';
	import type { Post } from '$lib/types';

	let posts: Post[] = [];
	let loading = true;
	let loadingMore = false;
	let hasMore = true;
	let page = 1;

	const inlineAds = [
		{ id: 'ad-1', title: 'Sponsorlu', text: 'Yeni içerik üreticilerini keşfet.', cta: 'Keşfet' },
		{ id: 'ad-2', title: 'Sponsorlu', text: 'Özel içerikler için premium paket.', cta: 'İncele' },
		{ id: 'ad-3', title: 'Sponsorlu', text: 'Canlı yayınları kaçırma.', cta: 'Canlıya Git' },
	];

	async function loadPosts() {
		try {
			const response = await api.posts.getFeed(page, 20);
			posts = [...posts, ...response.items];
			hasMore = response.items.length === 20;
		} catch (err) {
			console.error('Failed to load posts:', err);
		} finally {
			loading = false;
			loadingMore = false;
		}
	}

	async function loadMore() {
		if (loadingMore || !hasMore) return;
		loadingMore = true;
		page++;
		await loadPosts();
	}

	async function handleLike(e: CustomEvent<string>) {
		const postId = e.detail;
		try {
			await api.posts.like(postId);
			posts = posts.map((p) =>
				p.id === postId
					? { ...p, is_liked: !p.is_liked, likes_count: p.is_liked ? p.likes_count - 1 : p.likes_count + 1 }
					: p
			);
		} catch (err) {
			console.error('Failed to like post:', err);
		}
	}

	async function handleBookmark(e: CustomEvent<string>) {
		const postId = e.detail;
		try {
			await api.posts.bookmark(postId);
			posts = posts.map((p) =>
				p.id === postId ? { ...p, is_bookmarked: !p.is_bookmarked } : p
			);
		} catch (err) {
			console.error('Failed to bookmark post:', err);
		}
	}

	onMount(() => {
		loadPosts();
	});
</script>

<svelte:head>
	<title>Akış | SadeceFanlar</title>
</svelte:head>

<div class="p-4 space-y-4">
	<!-- Create Post CTA -->
	{#if $authStore.user}
		<div class="bg-white dark:bg-neutral-900 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-800 p-4">
			<a
				href="/new-post"
				class="flex items-center gap-3 text-neutral-400 hover:text-neutral-500 transition-colors"
			>
				<div class="w-10 h-10 rounded-full bg-neutral-100 dark:bg-neutral-800" />
				<span>Aklınızdan ne geçiyor?</span>
			</a>
		</div>
	{/if}

	<!-- Posts Feed -->
	{#if loading}
		{#each Array(3) as _}
			<div class="bg-white dark:bg-neutral-900 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-800 p-4 space-y-4">
				<div class="flex items-center gap-3">
					<Skeleton variant="circular" width="48px" height="48px" />
					<div class="flex-1">
						<Skeleton width="120px" />
						<Skeleton width="80px" class="mt-1" />
					</div>
				</div>
				<Skeleton lines={2} />
				<Skeleton variant="rectangular" height="300px" />
			</div>
		{/each}
	{:else if posts.length === 0}
		<div class="text-center py-12">
			<p class="text-4xl mb-4">📭</p>
			<h2 class="text-xl font-semibold text-neutral-900 dark:text-white mb-2">
				Akışınız boş
			</h2>
			<p class="text-neutral-500 mb-4">
				İçerik üreticilerine abone olarak gönderilerini burada görün.
			</p>
			<Button href="/explore">İçerik Üreticilerini Keşfet</Button>
		</div>
	{:else}
		{#each posts as post, index (post.id)}
			<PostCard
				{post}
				on:like={handleLike}
				on:bookmark={handleBookmark}
				on:comment={(e) => window.location.href = `/post/${e.detail}`}
				on:unlock={(e) => console.log('unlock', e.detail)}
				on:tip={(e) => console.log('tip', e.detail)}
			/>

			{#if (index + 1) % 4 === 0}
				{#each inlineAds.slice(0, 1) as ad (ad.id)}
					<div class="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 p-4">
						<div class="text-xs text-neutral-400">{ad.title}</div>
						<div class="mt-1 text-sm font-semibold text-neutral-900 dark:text-white">{ad.text}</div>
						<button class="mt-3 inline-flex items-center rounded-lg border border-neutral-200 dark:border-neutral-700 px-3 py-1 text-xs text-neutral-700 dark:text-neutral-200">
							{ad.cta}
						</button>
					</div>
				{/each}
			{/if}
		{/each}

		<!-- Load More -->
		{#if hasMore}
			<div class="flex justify-center py-4">
				{#if loadingMore}
					<Spinner />
				{:else}
					<Button variant="ghost" on:click={loadMore}>Daha Fazla Yükle</Button>
				{/if}
			</div>
		{/if}
	{/if}
</div>
