<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api';
	import { authStore } from '$lib/stores/auth';
	import { PostCard } from '$lib/components/features';
	import { Avatar, Button, Spinner } from '$lib/components/ui';
	import { timeAgo } from '$lib/utils';
	import type { Post } from '$lib/types';

	let post: Post | null = null;
	let comments: any[] = [];
	let loading = true;
	let notFound = false;
	let newComment = '';
	let sending = false;

	$: postId = $page.params.id;

	async function load() {
		loading = true;
		notFound = false;
		try {
			post = await api.posts.get(postId);
			const c = await api.posts.getComments(postId);
			comments = c.items;
		} catch {
			notFound = true;
		} finally {
			loading = false;
		}
	}

	async function submitComment() {
		if (!newComment.trim() || sending) return;
		sending = true;
		try {
			await api.posts.addComment(postId, newComment.trim());
			newComment = '';
			const c = await api.posts.getComments(postId);
			comments = c.items;
		} catch (e: any) {
			alert(e.message || 'Yorum gönderilemedi');
		} finally {
			sending = false;
		}
	}

	async function handleLike(e: CustomEvent<string>) {
		try {
			await api.posts.like(e.detail);
			if (post) post = { ...post, is_liked: !post.is_liked, likes_count: post.is_liked ? post.likes_count - 1 : post.likes_count + 1 };
		} catch {}
	}

	onMount(load);
</script>

<svelte:head>
	<title>Gönderi | SadeceFanlar</title>
	<meta name="robots" content="noindex, nofollow" />
</svelte:head>

<div class="py-2">
	<button class="text-sm text-neutral-500 hover:text-neutral-800 dark:hover:text-neutral-300 mb-4" on:click={() => history.back()}>
		← Geri
	</button>

	{#if loading}
		<div class="flex justify-center py-16"><Spinner size="lg" /></div>
	{:else if notFound || !post}
		<div class="text-center py-16">
			<p class="text-lg font-medium mb-2">Gönderi bulunamadı</p>
			<p class="text-neutral-500 mb-4">Bu gönderi silinmiş veya erişiminiz yok olabilir.</p>
			<Button href="/">Ana sayfaya dön</Button>
		</div>
	{:else}
		<PostCard {post} on:like={handleLike} on:tip={() => goto(`/${(post?.author ?? post?.user)?.username}`)} />

		<div class="mt-6">
			<h2 class="text-sm font-semibold text-neutral-500 mb-3">Yorumlar ({comments.length})</h2>

			{#if $authStore.user}
				<div class="flex gap-2 mb-5">
					<Avatar src={$authStore.user.avatar_url} alt={$authStore.user.display_name} size="sm" />
					<div class="flex-1 flex gap-2">
						<input
							class="flex-1 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-transparent px-3 py-2 text-sm"
							placeholder="Yorum yaz..."
							bind:value={newComment}
							on:keydown={(e) => e.key === 'Enter' && submitComment()}
						/>
						<Button size="sm" on:click={submitComment} disabled={sending}>Gönder</Button>
					</div>
				</div>
			{/if}

			{#if comments.length === 0}
				<p class="text-sm text-neutral-500 py-6 text-center">Henüz yorum yok.</p>
			{:else}
				<div class="space-y-4">
					{#each comments as c}
						<div class="flex gap-2">
							<Avatar src={c.author?.avatar_url ?? c.user?.avatar_url} alt={c.author?.display_name} size="sm" />
							<div class="flex-1">
								<div class="rounded-lg bg-neutral-100 dark:bg-neutral-800 px-3 py-2">
									<p class="text-sm font-medium">{c.author?.display_name ?? c.author?.username ?? c.user?.username ?? 'Kullanıcı'}</p>
									<p class="text-sm text-neutral-700 dark:text-neutral-300">{c.text ?? c.content}</p>
								</div>
								<p class="text-xs text-neutral-400 mt-1">{timeAgo(c.created_at)}</p>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	{/if}
</div>
