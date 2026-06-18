<script lang="ts">
	import { page } from '$app/stores';
	import { authStore, logout } from '$lib/stores/auth';
	import { theme } from '$lib/stores/theme';
	import { Avatar, Button } from '$lib/components/ui';
	import { cn } from '$lib/utils';
	import { isAdmin } from '$lib/utils/auth';

	$: user = $authStore.user;
	$: currentPath = $page.url.pathname;
	$: isLanding = currentPath === '/' && !user;

	const navItems = [
		{ href: '/', label: 'Ana Sayfa' },
		{ href: '/explore', label: 'Keşfet' },
		{ href: '/messages', label: 'Mesajlar', auth: true },
		{ href: '/notifications', label: 'Bildirimler', auth: true },
		{ href: '/wallet', label: 'Cüzdan', auth: true },
		{ href: '/support', label: 'Destek', auth: true },
	];

	function navClass(href: string) {
		const active = href === '/' ? currentPath === '/' : currentPath.startsWith(href);
		return cn(
			'block px-3 py-2 text-sm rounded-md transition-colors',
			active
				? 'bg-neutral-100 dark:bg-neutral-800 text-neutral-900 dark:text-white font-medium'
				: 'text-neutral-600 dark:text-neutral-400 hover:bg-neutral-50 dark:hover:bg-neutral-800/60'
		);
	}
</script>

<div class="min-h-screen bg-white dark:bg-neutral-950 text-neutral-900 dark:text-neutral-100">
	<aside class="hidden lg:fixed lg:inset-y-0 lg:left-0 lg:flex lg:w-56 lg:flex-col border-r border-neutral-200 dark:border-neutral-800">
		<div class="flex flex-col h-full px-4 py-5">
			<a href="/" class="px-3 mb-8 text-lg font-semibold tracking-tight">SadeceFanlar</a>

			<nav class="flex-1 space-y-1">
				{#each navItems as item}
					{#if !item.auth || user}
						<a href={item.href} class={navClass(item.href)}>{item.label}</a>
					{/if}
				{/each}

				{#if user}
					<a href="/{user.username}" class={navClass(`/${user.username}`)}>Profilim</a>
					<a href="/settings" class={navClass('/settings')}>Ayarlar</a>
					{#if isAdmin(user)}
						<a href="/settings?tab=site" class={navClass('/settings?tab=site')}>Site Ayarları</a>
					{/if}
				{/if}
			</nav>

			<button
				type="button"
				class="flex items-center gap-2 w-full px-3 py-2 mb-2 text-sm text-neutral-600 dark:text-neutral-400 hover:bg-neutral-50 dark:hover:bg-neutral-800/60 rounded-md transition-colors"
				on:click={() => theme.toggle()}
			>
				{#if $theme === 'dark'}☀️ Aydınlık tema{:else}🌙 Karanlık tema{/if}
			</button>

			<div class="pt-4 border-t border-neutral-200 dark:border-neutral-800">
				{#if user}
					<div class="flex items-center gap-3 px-3 py-2 mb-3">
						<Avatar src={user.avatar_url} alt={user.display_name} size="sm" />
						<div class="min-w-0">
							<p class="text-sm font-medium truncate">{user.display_name || user.username}</p>
							<p class="text-xs text-neutral-500 truncate">@{user.username}</p>
						</div>
					</div>
					{#if user.is_creator}
						<Button href="/new-post" class="w-full mb-2" size="sm">Yeni gönderi</Button>
					{/if}
					<button
						type="button"
						class="w-full text-left px-3 py-2 text-sm text-neutral-500 hover:text-neutral-900 dark:hover:text-white"
						on:click={() => { logout(); window.location.href = '/'; }}
					>
						Çıkış yap
					</button>
				{:else}
					<div class="space-y-2">
						<Button href="/login" class="w-full" size="sm">Giriş yap</Button>
						<Button href="/register" variant="outline" class="w-full" size="sm">Kayıt ol</Button>
					</div>
				{/if}
			</div>
		</div>
	</aside>

	<header class="lg:hidden sticky top-0 z-40 border-b border-neutral-200 dark:border-neutral-800 bg-white/95 dark:bg-neutral-950/95 backdrop-blur">
		<div class="flex items-center justify-between h-14 px-4">
			<a href="/" class="font-semibold">SadeceFanlar</a>
			{#if user}
				<div class="flex items-center gap-3 text-sm">
					<a href="/wallet" class="text-neutral-600 dark:text-neutral-300">Cüzdan</a>
					<a href="/settings" class="text-neutral-600 dark:text-neutral-300">Ayarlar</a>
				</div>
			{:else}
				<Button href="/login" size="sm">Giriş</Button>
			{/if}
		</div>
	</header>

	<nav class="lg:hidden fixed bottom-0 inset-x-0 z-40 border-t border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-950">
		<div class="grid grid-cols-5 h-14 text-xs">
			{#each navItems.slice(0, 4) as item}
				{#if !item.auth || user}
					<a href={item.href} class="flex flex-col items-center justify-center gap-0.5 text-neutral-500">
						<span class={currentPath === item.href || (item.href !== '/' && currentPath.startsWith(item.href)) ? 'text-neutral-900 dark:text-white font-medium' : ''}>
							{item.label}
						</span>
					</a>
				{/if}
			{/each}
			{#if user}
				<a href="/wallet" class="flex flex-col items-center justify-center text-neutral-500">
					<span class={currentPath.startsWith('/wallet') ? 'text-neutral-900 dark:text-white font-medium' : ''}>Cüzdan</span>
				</a>
			{:else}
				<a href="/login" class="flex flex-col items-center justify-center text-neutral-500">Giriş</a>
			{/if}
		</div>
	</nav>

	<main class="lg:pl-56 pt-0 pb-16 lg:pb-0">
		<div class={isLanding ? 'w-full' : 'max-w-3xl mx-auto px-4 py-6'}>
			<slot />
		</div>
	</main>
</div>
