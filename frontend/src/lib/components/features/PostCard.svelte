<script lang="ts">
	import { cn, formatCurrency, timeAgo } from '$lib/utils';
	import { Avatar, Badge, Button, Dropdown } from '$lib/components/ui';
	import type { Post } from '$lib/types';
	import { createEventDispatcher } from 'svelte';
	import { authStore } from '$lib/stores/auth';

	export let post: Post;
	export let showCreator = true;
	let className = '';
	export { className as class };

	const dispatch = createEventDispatcher();

	$: creator = post.author ?? post.user;
	$: isLocked = (post.is_ppv || post.is_premium) && !post.is_unlocked;
	$: isOwner = $authStore.user?.id === (creator?.id ?? post.user_id);
	$: mediaCount = post.media?.length || 0;
	$: currentMediaIndex = 0;

	const dropdownItems = [
		{ id: 'share', label: 'Paylaş', icon: '📤' },
		{ id: 'report', label: 'Şikayet Et', icon: '🚩', danger: true },
		...(isOwner
			? [
					{ id: 'divider', label: '', divider: true },
					{ id: 'edit', label: 'Düzenle', icon: '✏️' },
					{ id: 'delete', label: 'Sil', icon: '🗑️', danger: true },
			  ]
			: []),
	];

	function handleLike() {
		dispatch('like', post.id);
	}

	function handleComment() {
		dispatch('comment', post.id);
	}

	function handleBookmark() {
		dispatch('bookmark', post.id);
	}

	function handleUnlock() {
		dispatch('unlock', post);
	}

	function handleTip() {
		dispatch('tip', post);
	}

	function handleDropdownSelect(e: CustomEvent<string>) {
		dispatch(e.detail, post);
	}

	function nextMedia() {
		if (currentMediaIndex < mediaCount - 1) {
			currentMediaIndex++;
		}
	}

	function prevMedia() {
		if (currentMediaIndex > 0) {
			currentMediaIndex--;
		}
	}
</script>

<article
	class={cn(
		'bg-white dark:bg-neutral-900 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-800 overflow-hidden',
		className
	)}
>
	<!-- Header -->
	{#if showCreator}
		<div class="p-4 flex items-center justify-between">
			<a href="/{creator?.username}" class="flex items-center gap-3 group">
				<Avatar src={creator?.avatar_url} alt={creator?.display_name} size="md" />
				<div>
					<div class="flex items-center gap-1">
						<span class="font-semibold text-neutral-900 dark:text-white group-hover:text-primary transition-colors">
							{creator?.display_name || creator?.username}
						</span>
						{#if creator?.is_verified_creator}
							<Badge variant="primary" class="text-xs">✓</Badge>
						{/if}
					</div>
					<p class="text-sm text-neutral-500">@{creator?.username} · {timeAgo(post.created_at)}</p>
				</div>
			</a>
			<Dropdown items={dropdownItems} on:select={handleDropdownSelect} />
		</div>
	{/if}

	<!-- Content -->
	{#if post.text ?? post.content}
		<div class="px-4 pb-3">
			<p class="text-neutral-800 dark:text-neutral-200 whitespace-pre-wrap">{post.text ?? post.content}</p>
		</div>
	{/if}

	<!-- Media -->
	{#if post.media && post.media.length > 0}
		<div class="relative aspect-square bg-neutral-100 dark:bg-neutral-800">
			{#if isLocked}
				<!-- Locked content -->
				<div class="absolute inset-0 flex flex-col items-center justify-center bg-neutral-900/80 backdrop-blur-xl">
					<div class="text-4xl mb-4">🔒</div>
					<p class="text-white text-lg font-medium mb-2">Premium İçerik</p>
					<p class="text-neutral-400 mb-4">{formatCurrency(post.ppv_price ?? post.price ?? 0)} ile kilidi aç</p>
					<Button on:click={handleUnlock}>Kilidi Aç</Button>
				</div>
				<!-- Blurred thumbnail -->
				{#if post.media[0].blur_url}
					<img
						src={post.media[0].blur_url}
						alt="Locked content"
						class="w-full h-full object-cover filter blur-xl"
					/>
				{/if}
			{:else}
				<!-- Unlocked media carousel -->
				{#if post.media[currentMediaIndex].type === 'video'}
					<video
						src={post.media[currentMediaIndex].url}
						controls
						class="w-full h-full object-contain bg-black"
						poster={post.media[currentMediaIndex].thumbnail_url}
					>
						<track kind="captions" />
					</video>
				{:else}
					<img
						src={post.media[currentMediaIndex].url}
						alt="Post media"
						class="w-full h-full object-cover"
					/>
				{/if}

				<!-- Media navigation -->
				{#if mediaCount > 1}
					<div class="absolute inset-x-0 top-1/2 -translate-y-1/2 flex justify-between px-2">
						<button
							type="button"
							class={cn(
								'p-2 rounded-full bg-black/50 text-white hover:bg-black/70 transition-colors',
								currentMediaIndex === 0 && 'opacity-0 pointer-events-none'
							)}
							on:click={prevMedia}
						>
							←
						</button>
						<button
							type="button"
							class={cn(
								'p-2 rounded-full bg-black/50 text-white hover:bg-black/70 transition-colors',
								currentMediaIndex === mediaCount - 1 && 'opacity-0 pointer-events-none'
							)}
							on:click={nextMedia}
						>
							→
						</button>
					</div>

					<!-- Media indicators -->
					<div class="absolute bottom-4 inset-x-0 flex justify-center gap-1">
						{#each post.media as _, i}
							<button
								type="button"
								class={cn(
									'w-2 h-2 rounded-full transition-colors',
									i === currentMediaIndex ? 'bg-white' : 'bg-white/50'
								)}
								on:click={() => (currentMediaIndex = i)}
							/>
						{/each}
					</div>
				{/if}
			{/if}
		</div>
	{/if}

	<!-- Actions -->
	<div class="p-4 flex items-center justify-between border-t border-neutral-100 dark:border-neutral-800">
		<div class="flex items-center gap-4">
			<button
				type="button"
				class={cn(
					'flex items-center gap-1 text-sm transition-colors',
					post.is_liked ? 'text-red-500' : 'text-neutral-500 hover:text-red-500'
				)}
				on:click={handleLike}
			>
				<span class="text-xl">{post.is_liked ? '❤️' : '🤍'}</span>
				<span>{post.likes_count || 0}</span>
			</button>

			<button
				type="button"
				class="flex items-center gap-1 text-sm text-neutral-500 hover:text-primary transition-colors"
				on:click={handleComment}
			>
				<span class="text-xl">💬</span>
				<span>{post.comments_count || 0}</span>
			</button>

			<button
				type="button"
				class="flex items-center gap-1 text-sm text-neutral-500 hover:text-green-500 transition-colors"
				on:click={handleTip}
			>
				<span class="text-xl">💰</span>
				<span>Bahşiş</span>
			</button>
		</div>

		<button
			type="button"
			class={cn(
				'text-xl transition-colors',
				post.is_bookmarked ? 'text-yellow-500' : 'text-neutral-400 hover:text-yellow-500'
			)}
			on:click={handleBookmark}
		>
			{post.is_bookmarked ? '⭐' : '☆'}
		</button>
	</div>
</article>
