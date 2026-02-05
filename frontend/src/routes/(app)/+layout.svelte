<script lang="ts">
	import { page } from '$app/stores';
	import { authStore, logout } from '$lib/stores/auth';
	import { Avatar, Badge, Button, Dropdown } from '$lib/components/ui';
	import { cn } from '$lib/utils';

	$: user = $authStore.user;
	$: currentPath = $page.url.pathname;

	const navItems = [
		{ href: '/', label: 'Home', icon: '🏠' },
		{ href: '/explore', label: 'Explore', icon: '🔍' },
		{ href: '/messages', label: 'Messages', icon: '💬', auth: true },
		{ href: '/notifications', label: 'Notifications', icon: '🔔', auth: true },
	];

	const userMenuItems = [
		{ id: 'profile', label: 'My Profile', icon: '👤' },
		{ id: 'settings', label: 'Settings', icon: '⚙️' },
		{ id: 'wallet', label: 'Wallet', icon: '💰' },
		{ id: 'divider', label: '', divider: true },
		{ id: 'logout', label: 'Logout', icon: '🚪', danger: true },
	];

	function handleUserMenuSelect(e: CustomEvent<string>) {
		switch (e.detail) {
			case 'profile':
				window.location.href = `/${user?.username}`;
				break;
			case 'settings':
				window.location.href = '/settings';
				break;
			case 'wallet':
				window.location.href = '/wallet';
				break;
			case 'logout':
				logout();
				window.location.href = '/';
				break;
		}
	}
</script>

<div class="min-h-screen bg-neutral-50 dark:bg-neutral-950">
	<!-- Desktop Sidebar -->
	<aside class="hidden lg:fixed lg:inset-y-0 lg:left-0 lg:flex lg:w-64 lg:flex-col">
		<div class="flex flex-col flex-grow border-r border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 pt-5 pb-4 overflow-y-auto">
			<!-- Logo -->
			<div class="flex items-center flex-shrink-0 px-6">
				<a href="/" class="text-2xl font-bold text-primary">
					SadeceFanlar
				</a>
			</div>

			<!-- Navigation -->
			<nav class="mt-8 flex-1 px-4 space-y-1">
				{#each navItems as item}
					{#if !item.auth || user}
						<a
							href={item.href}
							class={cn(
								'flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-colors',
								currentPath === item.href
									? 'bg-primary/10 text-primary'
									: 'text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-800'
							)}
						>
							<span class="text-xl">{item.icon}</span>
							<span>{item.label}</span>
						</a>
					{/if}
				{/each}

				{#if user}
					<a
						href="/{user.username}"
						class={cn(
							'flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-colors',
							currentPath === `/${user.username}`
								? 'bg-primary/10 text-primary'
								: 'text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-800'
						)}
					>
						<span class="text-xl">👤</span>
						<span>Profile</span>
					</a>
				{/if}
			</nav>

			<!-- User Section -->
			<div class="px-4 pb-4">
				{#if user}
					<Button href="/new-post" class="w-full mb-4">
						+ New Post
					</Button>
					<Dropdown items={userMenuItems} align="left" on:select={handleUserMenuSelect}>
						<button
							slot="trigger"
							type="button"
							class="flex items-center gap-3 w-full p-3 rounded-xl hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
						>
							<Avatar src={user.avatar_url} alt={user.display_name} size="sm" />
							<div class="flex-1 text-left">
								<p class="text-sm font-medium text-neutral-900 dark:text-white truncate">
									{user.display_name}
								</p>
								<p class="text-xs text-neutral-500 truncate">@{user.username}</p>
							</div>
							<span class="text-neutral-400">⋮</span>
						</button>
					</Dropdown>
				{:else}
					<div class="space-y-2">
						<Button href="/login" class="w-full">Login</Button>
						<Button href="/register" variant="outline" class="w-full">Sign Up</Button>
					</div>
				{/if}
			</div>
		</div>
	</aside>

	<!-- Mobile Header -->
	<header class="lg:hidden fixed top-0 inset-x-0 z-40 bg-white dark:bg-neutral-900 border-b border-neutral-200 dark:border-neutral-800">
		<div class="flex items-center justify-between h-16 px-4">
			<a href="/" class="text-xl font-bold text-primary">SF</a>
			
			{#if user}
				<Dropdown items={userMenuItems} on:select={handleUserMenuSelect}>
					<button slot="trigger" type="button" class="p-1">
						<Avatar src={user.avatar_url} alt={user.display_name} size="sm" />
					</button>
				</Dropdown>
			{:else}
				<Button href="/login" size="sm">Login</Button>
			{/if}
		</div>
	</header>

	<!-- Mobile Bottom Navigation -->
	<nav class="lg:hidden fixed bottom-0 inset-x-0 z-40 bg-white dark:bg-neutral-900 border-t border-neutral-200 dark:border-neutral-800 safe-area-pb">
		<div class="flex items-center justify-around h-16">
			{#each navItems as item}
				{#if !item.auth || user}
					<a
						href={item.href}
						class={cn(
							'flex flex-col items-center gap-1 px-4 py-2 transition-colors',
							currentPath === item.href
								? 'text-primary'
								: 'text-neutral-400'
						)}
					>
						<span class="text-xl">{item.icon}</span>
						<span class="text-xs">{item.label}</span>
					</a>
				{/if}
			{/each}
			{#if user}
				<a
					href="/new-post"
					class="flex flex-col items-center gap-1 px-4 py-2 text-primary"
				>
					<span class="text-xl">➕</span>
					<span class="text-xs">Post</span>
				</a>
			{/if}
		</div>
	</nav>

	<!-- Main Content -->
	<main class="lg:pl-64 pt-16 lg:pt-0 pb-20 lg:pb-0">
		<div class="max-w-2xl mx-auto">
			<slot />
		</div>
	</main>
</div>

<style>
	.safe-area-pb {
		padding-bottom: env(safe-area-inset-bottom);
	}
</style>
