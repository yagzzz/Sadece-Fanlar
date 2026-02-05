<script lang="ts">
	import { cn, timeAgo } from '$lib/utils';
	import { Avatar } from '$lib/components/ui';
	import type { Message } from '$lib/types';
	import { authStore } from '$lib/stores/auth';

	export let message: Message;
	let className = '';
	export { className as class };

	$: isMine = message.sender_id === $authStore.user?.id;
</script>

<div
	class={cn(
		'flex gap-2 max-w-[80%]',
		isMine ? 'ml-auto flex-row-reverse' : 'mr-auto',
		className
	)}
>
	{#if !isMine}
		<Avatar src={message.sender?.avatar_url} alt={message.sender?.display_name} size="sm" />
	{/if}

	<div>
		<div
			class={cn(
				'rounded-2xl px-4 py-2',
				isMine
					? 'bg-primary text-white rounded-br-md'
					: 'bg-neutral-100 dark:bg-neutral-800 text-neutral-900 dark:text-white rounded-bl-md'
			)}
		>
			{#if message.media && message.media.length > 0}
				<div class="mb-2">
					{#each message.media as media}
						{#if media.type === 'image'}
							<img
								src={media.url}
								alt="Attachment"
								class="rounded-lg max-w-xs max-h-64 object-cover"
							/>
						{:else if media.type === 'video'}
							<video
								src={media.url}
								controls
								class="rounded-lg max-w-xs max-h-64"
								poster={media.thumbnail_url}
							>
								<track kind="captions" />
							</video>
						{/if}
					{/each}
				</div>
			{/if}

			{#if message.content}
				<p class="whitespace-pre-wrap break-words">{message.content}</p>
			{/if}

			{#if message.price && !message.is_unlocked}
				<div class="mt-2 p-2 bg-black/10 rounded-lg text-center">
					<p class="text-sm">🔒 Premium content</p>
					<p class="text-xs opacity-75">Unlock for ${message.price}</p>
				</div>
			{/if}
		</div>

		<div
			class={cn(
				'text-xs text-neutral-400 mt-1',
				isMine ? 'text-right' : 'text-left'
			)}
		>
			{timeAgo(message.created_at)}
			{#if isMine && message.is_read}
				<span class="ml-1">✓✓</span>
			{/if}
		</div>
	</div>
</div>
