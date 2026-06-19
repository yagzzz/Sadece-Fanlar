<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { api } from '$lib/api';
	import { wsUrl } from '$lib/api/client';
	import { authStore } from '$lib/stores/auth';
	import { MessageBubble } from '$lib/components/features';
	import { Avatar, Button, Input, Spinner, Skeleton } from '$lib/components/ui';
	import { cn, timeAgo } from '$lib/utils';
	import type { Conversation, Message } from '$lib/types';

	let conversations: Conversation[] = [];
	let selectedConversation: Conversation | null = null;
	let messages: Message[] = [];
	let newMessage = '';
	let loading = true;
	let loadingMessages = false;
	let sending = false;
	let messagesContainer: HTMLElement;
	let ws: WebSocket | null = null;

	async function loadConversations() {
		loading = true;
		try {
			conversations = await api.messages.getConversations();
		} catch (err) {
			console.error('Failed to load conversations:', err);
		} finally {
			loading = false;
		}
	}

	async function selectConversation(conversation: Conversation) {
		selectedConversation = conversation;
		loadingMessages = true;

		try {
			const response = await api.messages.getMessages(conversation.id);
			messages = response.items.reverse();

			// Mark as read
			await api.messages.markAsRead(conversation.id);

			// Connect WebSocket
			connectWebSocket(conversation.id);

			// Scroll to bottom
			setTimeout(scrollToBottom, 100);
		} catch (err) {
			console.error('Failed to load messages:', err);
		} finally {
			loadingMessages = false;
		}
	}

	function connectWebSocket(conversationId: string) {
		if (ws) ws.close();

		const token = localStorage.getItem('access_token');
		ws = new WebSocket(wsUrl(`/api/v1/messages/ws/${conversationId}?token=${token}`));

		ws.onmessage = (event) => {
			const message = JSON.parse(event.data);
			messages = [...messages, message];
			scrollToBottom();
		};

		ws.onerror = (error) => {
			console.error('WebSocket error:', error);
		};
	}

	async function sendMessage() {
		if (!newMessage.trim() || !selectedConversation || sending) return;

		sending = true;
		const content = newMessage;
		newMessage = '';

		try {
			const message = await api.messages.send(selectedConversation.id, { content });
			messages = [...messages, message];
			scrollToBottom();
		} catch (err) {
			console.error('Failed to send message:', err);
			newMessage = content;
		} finally {
			sending = false;
		}
	}

	function scrollToBottom() {
		if (messagesContainer) {
			messagesContainer.scrollTop = messagesContainer.scrollHeight;
		}
	}

	function handleKeyDown(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			sendMessage();
		}
	}

	onMount(() => {
		loadConversations();
	});

	onDestroy(() => {
		if (ws) ws.close();
	});
</script>

<svelte:head>
	<title>Mesajlar | SadeceFanlar</title>
</svelte:head>

<div class="flex h-[calc(100vh-4rem)] lg:h-screen">
	<!-- Conversations List -->
	<div
		class={cn(
			'w-full md:w-80 border-r border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 flex flex-col',
			selectedConversation && 'hidden md:flex'
		)}
	>
		<div class="p-4 border-b border-neutral-200 dark:border-neutral-800">
			<h1 class="text-xl font-bold text-neutral-900 dark:text-white">Mesajlar</h1>
		</div>

		<div class="flex-1 overflow-y-auto">
			{#if loading}
				{#each Array(5) as _}
					<div class="flex items-center gap-3 p-4 border-b border-neutral-100 dark:border-neutral-800">
						<Skeleton variant="circular" width="48px" height="48px" />
						<div class="flex-1">
							<Skeleton width="60%" />
							<Skeleton width="80%" class="mt-1" />
						</div>
					</div>
				{/each}
			{:else if conversations.length === 0}
				<div class="text-center py-12 px-4">
					<p class="text-4xl mb-4">💬</p>
					<p class="text-neutral-500">Henüz mesaj yok</p>
					<Button href="/explore" variant="ghost" class="mt-4">
						Mesaj atacak içerik üreticisi bul
					</Button>
				</div>
			{:else}
				{#each conversations as conversation}
					<button
						type="button"
						class={cn(
							'w-full flex items-center gap-3 p-4 border-b border-neutral-100 dark:border-neutral-800 hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors text-left',
							selectedConversation?.id === conversation.id && 'bg-neutral-50 dark:bg-neutral-800'
						)}
						on:click={() => selectConversation(conversation)}
					>
						<Avatar
							src={conversation.other_user?.avatar_url}
							alt={conversation.other_user?.display_name}
							size="md"
						/>
						<div class="flex-1 min-w-0">
							<div class="flex items-center justify-between">
								<p class="font-medium text-neutral-900 dark:text-white truncate">
									{conversation.other_user?.display_name}
								</p>
								<span class="text-xs text-neutral-400">
									{conversation.last_message_at ? timeAgo(conversation.last_message_at) : ''}
								</span>
							</div>
							<p class="text-sm text-neutral-500 truncate">
								{typeof conversation.last_message === 'string'
									? conversation.last_message
									: conversation.last_message?.content || 'Sohbet başlat'}
							</p>
						</div>
						{#if conversation.unread_count > 0}
							<span class="w-5 h-5 bg-primary text-white text-xs rounded-full flex items-center justify-center">
								{conversation.unread_count}
							</span>
						{/if}
					</button>
				{/each}
			{/if}
		</div>
	</div>

	<!-- Chat Area -->
	<div
		class={cn(
			'flex-1 flex flex-col bg-neutral-50 dark:bg-neutral-950',
			!selectedConversation && 'hidden md:flex'
		)}
	>
		{#if selectedConversation}
			<!-- Chat Header -->
			<div class="flex items-center gap-3 p-4 border-b border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900">
				<button
					type="button"
					class="md:hidden text-neutral-400 hover:text-neutral-600"
					on:click={() => (selectedConversation = null)}
				>
					←
				</button>
				<a href="/{selectedConversation.other_user?.username}" class="flex items-center gap-3">
					<Avatar
						src={selectedConversation.other_user?.avatar_url}
						alt={selectedConversation.other_user?.display_name}
						size="md"
					/>
					<div>
						<p class="font-medium text-neutral-900 dark:text-white">
							{selectedConversation.other_user?.display_name}
						</p>
						<p class="text-xs text-neutral-500">
							@{selectedConversation.other_user?.username}
						</p>
					</div>
				</a>
			</div>

			<!-- Messages -->
			<div class="flex-1 overflow-y-auto p-4 space-y-4" bind:this={messagesContainer}>
				{#if loadingMessages}
					<div class="flex items-center justify-center py-8">
						<Spinner />
					</div>
				{:else}
					{#each messages as message (message.id)}
						<MessageBubble {message} />
					{/each}
				{/if}
			</div>

			<!-- Input Area -->
			<div class="p-4 border-t border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900">
				<form on:submit|preventDefault={sendMessage} class="flex items-center gap-2">
					<button
						type="button"
						class="p-2 text-neutral-400 hover:text-neutral-600 transition-colors"
					>
						📎
					</button>
					<input
						type="text"
						bind:value={newMessage}
						placeholder="Mesaj yaz..."
						class="flex-1 bg-neutral-100 dark:bg-neutral-800 rounded-full px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
						on:keydown={handleKeyDown}
					/>
					<Button type="submit" disabled={!newMessage.trim() || sending} size="icon">
						{sending ? '...' : '➤'}
					</Button>
				</form>
			</div>
		{:else}
			<!-- Empty State -->
			<div class="flex-1 flex items-center justify-center">
				<div class="text-center">
					<p class="text-6xl mb-4">💬</p>
					<p class="text-neutral-500">Mesajlaşmaya başlamak için bir sohbet seçin</p>
				</div>
			</div>
		{/if}
	</div>
</div>
