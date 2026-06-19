<script lang="ts">
	import { page } from '$app/stores';
	import { authStore, logout } from '$lib/stores/auth';
	import { theme } from '$lib/stores/theme';
	import { Avatar, Button, Icon } from '$lib/components/ui';
	import { cn } from '$lib/utils';
	import { isAdmin, isStaff } from '$lib/utils/auth';

	$: user = $authStore.user;
	$: currentPath = $page.url.pathname;
	$: isLanding = currentPath === '/' && !user;

	const navItems = [
		{ href: '/', label: 'Ana Sayfa', icon: 'home' },
		{ href: '/explore', label: 'Keşfet', icon: 'compass' },
		{ href: '/messages', label: 'Mesajlar', icon: 'message', auth: true },
		{ href: '/notifications', label: 'Bildirimler', icon: 'bell', auth: true },
		{ href: '/wallet', label: 'Cüzdan', icon: 'wallet', auth: true },
		{ href: '/support', label: 'Destek', icon: 'headset', auth: true }
	];

	function isActive(href: string): boolean {
		return href === '/' ? currentPath === '/' : currentPath.startsWith(href);
	}

	function navClass(href: string) {
		return cn(
			'flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition-colors',
			isActive(href)
				? 'bg-primary/10 text-primary font-medium'
				: 'text-muted-foreground hover:bg-muted hover:text-foreground'
		);
	}
</script>

<div class="min-h-screen bg-background text-foreground">
	<!-- Masaüstü kenar çubuğu -->
	<aside
		class="hidden lg:fixed lg:inset-y-0 lg:left-0 lg:flex lg:w-60 lg:flex-col border-r border-border bg-card"
	>
		<div class="flex flex-col h-full px-3 py-5">
			<a href="/" class="flex items-center gap-2 px-3 mb-7">
				<span class="grid place-items-center w-8 h-8 rounded-lg bg-primary text-primary-foreground font-bold">S</span>
				<span class="text-base font-semibold tracking-tight">Sadece Fanlar</span>
			</a>

			<nav class="flex-1 space-y-1">
				{#each navItems as item}
					{#if !item.auth || user}
						<a href={item.href} class={navClass(item.href)}>
							<Icon name={item.icon} size={18} />
							<span>{item.label}</span>
						</a>
					{/if}
				{/each}

				{#if user}
					<a href="/{user.username}" class={navClass(`/${user.username}`)}>
						<Icon name="user" size={18} />
						<span>Profilim</span>
					</a>
					<a href="/settings" class={navClass('/settings')}>
						<Icon name="settings" size={18} />
						<span>Ayarlar</span>
					</a>
					{#if isStaff(user)}
						<a href="/admin" class={navClass('/admin')}>
							<Icon name="shield" size={18} />
							<span>Yönetim</span>
						</a>
					{/if}
				{/if}
			</nav>

			<button
				type="button"
				class="flex items-center gap-3 w-full px-3 py-2 mb-2 text-sm text-muted-foreground hover:bg-muted hover:text-foreground rounded-lg transition-colors"
				on:click={() => theme.toggle()}
			>
				{#if $theme === 'dark'}
					<Icon name="sun" size={18} /><span>Aydınlık tema</span>
				{:else}
					<Icon name="moon" size={18} /><span>Karanlık tema</span>
				{/if}
			</button>

			<div class="pt-4 border-t border-border">
				{#if user}
					<a href="/{user.username}" class="flex items-center gap-3 px-3 py-2 mb-3 rounded-lg hover:bg-muted transition-colors">
						<Avatar src={user.avatar_url} alt={user.display_name} size="sm" />
						<div class="min-w-0">
							<p class="text-sm font-medium truncate">{user.display_name || user.username}</p>
							<p class="text-xs text-muted-foreground truncate">@{user.username}</p>
						</div>
					</a>
					{#if user.is_creator}
						<Button href="/new-post" class="w-full mb-2" size="sm">
							<Icon name="plus" size={16} class="mr-1.5" />Yeni gönderi
						</Button>
					{/if}
					<button
						type="button"
						class="flex items-center gap-3 w-full px-3 py-2 text-sm text-muted-foreground hover:text-foreground rounded-lg hover:bg-muted transition-colors"
						on:click={() => { logout(); window.location.href = '/'; }}
					>
						<Icon name="logout" size={18} /><span>Çıkış yap</span>
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

	<!-- Mobil üst bar -->
	<header
		class="lg:hidden sticky top-0 z-40 border-b border-border bg-background/90 backdrop-blur"
	>
		<div class="flex items-center justify-between h-14 px-4">
			<a href="/" class="flex items-center gap-2 font-semibold">
				<span class="grid place-items-center w-7 h-7 rounded-md bg-primary text-primary-foreground text-sm font-bold">S</span>
				Sadece Fanlar
			</a>
			<div class="flex items-center gap-1">
				<button type="button" class="p-2 text-muted-foreground hover:text-foreground" on:click={() => theme.toggle()} aria-label="Tema değiştir">
					<Icon name={$theme === 'dark' ? 'sun' : 'moon'} size={20} />
				</button>
				{#if user}
					<a href="/settings" class="p-2 text-muted-foreground hover:text-foreground" aria-label="Ayarlar"><Icon name="settings" size={20} /></a>
				{:else}
					<Button href="/login" size="sm">Giriş</Button>
				{/if}
			</div>
		</div>
	</header>

	<!-- Mobil alt navigasyon -->
	<nav class="lg:hidden fixed bottom-0 inset-x-0 z-40 border-t border-border bg-background">
		<div class="grid grid-cols-5 h-16">
			{#each navItems.slice(0, 5) as item}
				{#if !item.auth || user}
					<a
						href={item.href}
						class={cn(
							'flex flex-col items-center justify-center gap-1 text-[11px] transition-colors',
							isActive(item.href) ? 'text-primary' : 'text-muted-foreground'
						)}
					>
						<Icon name={item.icon} size={20} />
						<span>{item.label}</span>
					</a>
				{/if}
			{/each}
			{#if !user}
				<a href="/login" class="flex flex-col items-center justify-center gap-1 text-[11px] text-muted-foreground col-start-5">
					<Icon name="user" size={20} /><span>Giriş</span>
				</a>
			{/if}
		</div>
	</nav>

	<main class="lg:pl-60 pb-20 lg:pb-0">
		<div class={isLanding ? 'w-full' : 'max-w-3xl mx-auto px-4 py-6'}>
			<slot />
		</div>
	</main>
</div>
