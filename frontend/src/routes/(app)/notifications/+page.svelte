<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { api } from '$lib/api';
	import { wsUrl } from '$lib/api/client';
	import { Avatar, Button, Spinner, Switch, Tabs } from '$lib/components/ui';
	import { cn, timeAgo } from '$lib/utils';
	import type { Notification } from '$lib/types';

	let notifications: Notification[] = [];
	let loading = true;
	let activeTab = 'all';
	let ws: WebSocket | null = null;

	const tabs = [
		{ id: 'all', label: 'Tümü' },
		{ id: 'likes', label: '❤️ Beğeniler' },
		{ id: 'comments', label: '💬 Yorumlar' },
		{ id: 'subscriptions', label: '⭐ Abonelikler' },
		{ id: 'tips', label: '💰 Bahşişler' },
	];

	async function loadNotifications() {
		loading = true;
		try {
			const response = await api.notifications.list({
				type: activeTab !== 'all' ? activeTab : undefined,
			});
			notifications = response.items;
		} catch (err) {
			console.error('Failed to load notifications:', err);
		} finally {
			loading = false;
		}
	}

	async function markAsRead(id: string) {
		try {
			await api.notifications.markAsRead(id);
			notifications = notifications.map((n) =>
				n.id === id ? { ...n, is_read: true } : n
			);
		} catch (err) {
			console.error('Failed to mark as read:', err);
		}
	}

	async function markAllAsRead() {
		try {
			await api.notifications.markAllAsRead();
			notifications = notifications.map((n) => ({ ...n, is_read: true }));
		} catch (err) {
			console.error('Failed to mark all as read:', err);
		}
	}

	function connectWebSocket() {
		const token = localStorage.getItem('access_token');
		ws = new WebSocket(wsUrl(`/api/v1/notifications/ws?token=${token}`));

		ws.onmessage = (event) => {
			const notification = JSON.parse(event.data);
			notifications = [notification, ...notifications];
		};

		ws.onerror = (error) => {
			console.error('WebSocket error:', error);
		};
	}

	function getNotificationIcon(type: string): string {
		switch (type) {
			case 'like':
				return '❤️';
			case 'comment':
				return '💬';
			case 'subscription':
				return '⭐';
			case 'tip':
				return '💰';
			case 'follow':
				return '👤';
			case 'mention':
				return '@';
			default:
				return '🔔';
		}
	}

	function getNotificationLink(notification: Notification): string {
		switch (notification.type) {
			case 'like':
			case 'comment':
				return `/post/${notification.data?.post_id}`;
			case 'subscription':
			case 'follow':
				return `/${notification.actor?.username}`;
			case 'tip':
				return '/wallet';
			default:
				return '#';
		}
	}

	onMount(() => {
		loadNotifications();
		connectWebSocket();
	});

	onDestroy(() => {
		if (ws) ws.close();
	});

	$: if (activeTab) loadNotifications();
</script>

<svelte:head>
	<title>Bildirimler | SadeceFanlar</title>
</svelte:head>

<div class="p-4">
	<div class="flex items-center justify-between mb-6">
		<h1 class="text-2xl font-bold text-neutral-900 dark:text-white">Bildirimler</h1>
		{#if notifications.some((n) => !n.is_read)}
			<Button variant="ghost" size="sm" on:click={markAllAsRead}>
				Tümünü okundu işaretle
			</Button>
		{/if}
	</div>

	<Tabs {tabs} bind:activeTab>
		{#if loading}
			<div class="flex items-center justify-center py-12">
				<Spinner />
			</div>
		{:else if notifications.length === 0}
			<div class="text-center py-12">
				<p class="text-4xl mb-4">🔔</p>
				<p class="text-neutral-500">Henüz bildirim yok</p>
			</div>
		{:else}
			<div class="space-y-1">
				{#each notifications as notification (notification.id)}
					<a
						href={getNotificationLink(notification)}
						class={cn(
							'flex items-start gap-3 p-4 rounded-xl transition-colors',
							notification.is_read
								? 'bg-transparent hover:bg-neutral-100 dark:hover:bg-neutral-800'
								: 'bg-primary/5 hover:bg-primary/10'
						)}
						on:click={() => markAsRead(notification.id)}
					>
						<div class="relative">
							<Avatar
								src={notification.actor?.avatar_url}
								alt={notification.actor?.display_name}
								size="md"
							/>
							<span class="absolute -bottom-1 -right-1 text-sm">
								{getNotificationIcon(notification.type)}
							</span>
						</div>
						<div class="flex-1 min-w-0">
							<p class="text-sm text-neutral-900 dark:text-white">
								<span class="font-semibold">{notification.actor?.display_name}</span>
								{' '}
								{notification.message}
							</p>
							<p class="text-xs text-neutral-500 mt-1">
								{timeAgo(notification.created_at)}
							</p>
						</div>
						{#if !notification.is_read}
							<div class="w-2 h-2 bg-primary rounded-full mt-2" />
						{/if}
					</a>
				{/each}
			</div>
		{/if}
	</Tabs>
</div>
