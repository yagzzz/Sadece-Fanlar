<script lang="ts">
	import { cn, formatCurrency } from '$lib/utils';
	import { Avatar, Badge, Button } from '$lib/components/ui';
	import type { User } from '$lib/types';
	import { createEventDispatcher } from 'svelte';

	export let user: User;
	export let showStats = true;
	export let showSubscribe = true;
	let className = '';
	export { className as class };

	const dispatch = createEventDispatcher();

	function handleSubscribe() {
		dispatch('subscribe', user);
	}

	function handleMessage() {
		dispatch('message', user);
	}
</script>

<div
	class={cn(
		'bg-white dark:bg-neutral-900 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-800 overflow-hidden',
		className
	)}
>
	<!-- Cover Image -->
	<div class="relative h-24 bg-gradient-to-r from-primary/50 to-primary">
		{#if user.cover_url}
			<img src={user.cover_url} alt="Cover" class="w-full h-full object-cover" />
		{/if}
	</div>

	<!-- Profile Info -->
	<div class="px-4 pb-4">
		<div class="relative -mt-10 mb-3">
			<Avatar src={user.avatar_url} alt={user.display_name} size="lg" class="border-4 border-white dark:border-neutral-900" />
		</div>

		<div class="mb-3">
			<div class="flex items-center gap-1">
				<h3 class="font-semibold text-lg text-neutral-900 dark:text-white">
					{user.display_name}
				</h3>
				{#if user.is_verified}
					<Badge variant="primary" class="text-xs">✓</Badge>
				{/if}
			</div>
			<p class="text-neutral-500 text-sm">@{user.username}</p>
		</div>

		{#if user.bio}
			<p class="text-sm text-neutral-600 dark:text-neutral-400 mb-3 line-clamp-2">
				{user.bio}
			</p>
		{/if}

		{#if showStats}
			<div class="flex items-center gap-4 text-sm text-neutral-500 mb-4">
				<div>
					<span class="font-semibold text-neutral-900 dark:text-white">{user.posts_count || 0}</span>
					Posts
				</div>
				<div>
					<span class="font-semibold text-neutral-900 dark:text-white">{user.subscribers_count || 0}</span>
					Subscribers
				</div>
			</div>
		{/if}

		{#if showSubscribe}
			<div class="flex gap-2">
				{#if user.is_subscribed}
					<Button variant="secondary" class="flex-1" on:click={handleMessage}>
						💬 Message
					</Button>
				{:else}
					<Button class="flex-1" on:click={handleSubscribe}>
						Subscribe {#if user.subscription_price}
							· {formatCurrency(user.subscription_price)}/mo
						{:else}
							· Free
						{/if}
					</Button>
				{/if}
			</div>
		{/if}
	</div>
</div>
