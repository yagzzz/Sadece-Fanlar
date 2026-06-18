<script lang="ts">
	import { api } from '$lib/api';
	import { authStore } from '$lib/stores/auth';
	import { PostCard, Landing } from '$lib/components/features';
	import { Button, Spinner, Skeleton } from '$lib/components/ui';
	import type { Post } from '$lib/types';

	let posts: Post[] = [];
	let loading = true;
	let loadingMore = false;
	let hasMore = true;
	let page = 1;

	$: isReady = $authStore.initialized;
	$: isLoggedIn = !!$authStore.user;

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

	async function handleTip(e: CustomEvent<any>) {
		const post = e.detail;
		const recipientId = post?.author?.id ?? post?.user?.id ?? post?.user_id;
		if (!recipientId) return;
		const input = prompt('Bahşiş tutarı (TL):', '10');
		if (!input) return;
		const amount = parseFloat(input);
		if (!amount || amount <= 0) return;
		try {
			await api.payments.tip(recipientId, amount, { postId: post.id });
			alert('Bahşiş gönderildi, teşekkürler!');
		} catch (err: any) {
			const msg = err?.message || 'Bahşiş başarısız';
			if (msg.toLowerCase().includes('bakiye')) {
				if (confirm('Bakiyeniz yetersiz. Cüzdana gitmek ister misiniz?')) window.location.href = '/wallet';
			} else alert(msg);
		}
	}

	async function handleUnlock(e: CustomEvent<any>) {
		const post = e.detail;
		if (!post?.id) return;
		const price = post.ppv_price ?? post.price ?? 0;
		if (!confirm(`Bu içeriğin kilidini ${price} TL ile açmak istiyor musunuz?`)) return;
		try {
			await api.payments.unlockPost(post.id);
			posts = posts.map((p) => (p.id === post.id ? { ...p, is_unlocked: true } : p));
			alert('İçerik kilidi açıldı!');
		} catch (err: any) {
			const msg = err?.message || 'Kilit açma başarısız';
			if (msg.toLowerCase().includes('bakiye')) {
				if (confirm('Bakiyeniz yetersiz. Cüzdana gitmek ister misiniz?')) window.location.href = '/wallet';
			} else alert(msg);
		}
	}

	let started = false;
	// Auth durumu hazır olduğunda: giriş yapıldıysa akışı yükle,
	// yapılmadıysa tanıtım (landing) sayfasını göster.
	$: if (isReady) {
		if (isLoggedIn && !started) {
			started = true;
			loadPosts();
		} else if (!isLoggedIn) {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>{isLoggedIn ? 'Akış' : 'SadeceFanlar — Anonim, kripto tabanlı içerik platformu'} | SadeceFanlar</title>
</svelte:head>

{#if isReady && !isLoggedIn}
	<Landing />
{:else}
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
		{#each posts as post (post.id)}
			<PostCard
				{post}
				on:like={handleLike}
				on:bookmark={handleBookmark}
				on:comment={(e) => window.location.href = `/post/${e.detail}`}
				on:unlock={handleUnlock}
				on:tip={handleTip}
			/>
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
{/if}
