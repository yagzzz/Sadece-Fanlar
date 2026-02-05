<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { authStore } from '$lib/stores/auth';
	import { PostCard, SubscribeModal } from '$lib/components/features';
	import { Avatar, Badge, Button, Skeleton, Spinner, Tabs } from '$lib/components/ui';
	import { formatCurrency } from '$lib/utils';
	import type { User, Post } from '$lib/types';

	$: username = $page.params.username;

	let user: User | null = null;
	let posts: Post[] = [];
	let loading = true;
	let loadingPosts = true;
	let activeTab = 'posts';
	let showSubscribeModal = false;

	const tabs = [
		{ id: 'posts', label: '📝 Gönderiler' },
		{ id: 'media', label: '📷 Medya' },
		{ id: 'locked', label: '🔒 Kilitli' },
	];

	$: isOwnProfile = $authStore.user?.username === username;

	async function loadUser() {
		loading = true;
		try {
			user = await api.users.getByUsername(username);
		} catch (err) {
			console.error('Failed to load user:', err);
		} finally {
			loading = false;
		}
	}

	async function loadPosts() {
		if (!user) return;
		loadingPosts = true;
		try {
			const response = await api.posts.getByUser(user.username, {
				filter: activeTab === 'media' ? 'media' : activeTab === 'locked' ? 'locked' : undefined,
			});
			posts = response.items;
		} catch (err) {
			console.error('Failed to load posts:', err);
		} finally {
			loadingPosts = false;
		}
	}

	async function handleFollow() {
		if (!user) return;
		try {
			if (user.is_following) {
				await api.users.unfollow(user.username);
			} else {
				await api.users.follow(user.username);
			}
			user = { ...user, is_following: !user.is_following };
		} catch (err) {
			console.error('Failed to follow/unfollow:', err);
		}
	}

	function handleSubscribe() {
		showSubscribeModal = true;
	}

	onMount(() => {
		loadUser();
	});

	$: if (user) loadPosts();
	$: if (username) loadUser();
</script>

<svelte:head>
	<title>{user?.display_name || username} | SadeceFanlar</title>
	<meta name="description" content={user?.bio || `Check out ${username}'s profile on SadeceFanlar`} />
</svelte:head>

{#if loading}
	<div class="animate-pulse">
		<Skeleton variant="rectangular" height="200px" />
		<div class="p-4 -mt-16">
			<Skeleton variant="circular" width="100px" height="100px" />
			<Skeleton width="40%" class="mt-4" />
			<Skeleton width="30%" class="mt-2" />
			<Skeleton lines={2} class="mt-4" />
		</div>
	</div>
{:else if !user}
	<div class="text-center py-20">
		<p class="text-4xl mb-4">🤷</p>
		<h2 class="text-xl font-semibold text-neutral-900 dark:text-white mb-2">
			Kullanıcı bulunamadı
		</h2>
		<p class="text-neutral-500 mb-4">
			Aradığınız profil mevcut değil.
		</p>
		<Button href="/explore">İçerik Üreticilerini Keşfet</Button>
	</div>
{:else}
	<!-- Cover Image -->
	<div class="relative h-48 bg-gradient-to-r from-primary/50 to-primary">
		{#if user.cover_url}
			<img src={user.cover_url} alt="Cover" class="w-full h-full object-cover" />
		{/if}
	</div>

	<!-- Profile Header -->
	<div class="px-4 pb-4 -mt-16 relative">
		<div class="flex items-end gap-4 mb-4">
			<Avatar
				src={user.avatar_url}
				alt={user.display_name}
				size="lg"
				class="w-24 h-24 border-4 border-white dark:border-neutral-900"
			/>
			
			<div class="flex-1 flex items-center gap-2 pb-2">
				{#if isOwnProfile}
					<Button href="/settings" variant="outline" size="sm">
						Profili Düzenle
					</Button>
				{:else}
					{#if user.is_subscribed}
						<Button variant="secondary" size="sm" on:click={() => window.location.href = `/messages/${user?.id}`}>
							💬 Mesaj
						</Button>
					{:else}
						<Button size="sm" on:click={handleSubscribe}>
							Abone Ol
						</Button>
					{/if}
					<Button
						variant={user.is_following ? 'outline' : 'secondary'}
						size="sm"
						on:click={handleFollow}
					>
						{user.is_following ? 'Takip Ediliyor' : 'Takip Et'}
					</Button>
				{/if}
			</div>
		</div>

		<div class="mb-4">
			<div class="flex items-center gap-2">
				<h1 class="text-2xl font-bold text-neutral-900 dark:text-white">
					{user.display_name}
				</h1>
				{#if user.is_verified}
					<Badge variant="primary">✓ Doğrulanmış</Badge>
				{/if}
			</div>
			<p class="text-neutral-500">@{user.username}</p>
		</div>

		{#if user.bio}
			<p class="text-neutral-700 dark:text-neutral-300 mb-4 whitespace-pre-wrap">
				{user.bio}
			</p>
		{/if}

		<!-- Stats -->
		<div class="flex items-center gap-6 text-sm mb-4">
			<div>
				<span class="font-bold text-neutral-900 dark:text-white">{user.posts_count || 0}</span>
				<span class="text-neutral-500">gönderi</span>
			</div>
			<div>
				<span class="font-bold text-neutral-900 dark:text-white">{user.subscribers_count || 0}</span>
				<span class="text-neutral-500">abone</span>
			</div>
			<div>
				<span class="font-bold text-neutral-900 dark:text-white">{user.media_count || 0}</span>
				<span class="text-neutral-500">medya</span>
			</div>
		</div>

		<!-- Subscription Info -->
		{#if !isOwnProfile && !user.is_subscribed}
			<div class="bg-primary/5 border border-primary/20 rounded-xl p-4 mb-4">
				<div class="flex items-center justify-between">
					<div>
						<p class="font-medium text-neutral-900 dark:text-white">
							Tam erişim için abone olun
						</p>
						<p class="text-sm text-neutral-500">
							{user.subscription_price ? `${formatCurrency(user.subscription_price)}/ay` : 'Ücretsiz'}
						</p>
					</div>
					<Button on:click={handleSubscribe}>Şimdi Abone Ol</Button>
				</div>
			</div>
		{/if}
	</div>

	<!-- Posts Tabs -->
	<div class="px-4">
		<Tabs {tabs} bind:activeTab>
			{#if loadingPosts}
				<div class="space-y-4">
					{#each Array(3) as _}
						<div class="bg-white dark:bg-neutral-900 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-800 p-4 space-y-4">
							<Skeleton lines={2} />
							<Skeleton variant="rectangular" height="200px" />
						</div>
					{/each}
				</div>
			{:else if posts.length === 0}
				<div class="text-center py-12">
					<p class="text-4xl mb-4">📭</p>
					<p class="text-neutral-500">
						{activeTab === 'posts' ? 'Henüz gönderi yok.' : activeTab === 'media' ? 'Henüz medya içerikli gönderi yok.' : 'Kilitli içerik yok.'}
					</p>
				</div>
			{:else}
				<div class="space-y-4 pb-8">
					{#each posts as post (post.id)}
						<PostCard {post} showCreator={false} />
					{/each}
				</div>
			{/if}
		</Tabs>
	</div>

	<!-- Subscribe Modal -->
	{#if user}
		<SubscribeModal
			bind:open={showSubscribeModal}
			{user}
			on:subscribe={(e) => {
				showSubscribeModal = false;
				// Open payment modal
				console.log('Subscribe:', e.detail);
			}}
		/>
	{/if}
{/if}
