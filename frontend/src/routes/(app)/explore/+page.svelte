<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { UserCard } from '$lib/components/features';
	import { Button, Input, Spinner, Skeleton, Tabs } from '$lib/components/ui';
	import { debounce } from '$lib/utils';
	import type { User } from '$lib/types';

	let users: User[] = [];
	let loading = true;
	let searchQuery = '';
	let activeTab = 'featured';

	const tabs = [
		{ id: 'featured', label: 'Öne Çıkanlar' },
		{ id: 'new', label: 'Yeni' },
		{ id: 'popular', label: 'Popüler' },
	];

	async function loadUsers() {
		loading = true;
		try {
			const response = await api.users.explore({
				sort: activeTab,
				search: searchQuery || undefined,
				page: 1,
				limit: 20,
			});
			users = response.items;
		} catch (err) {
			console.error('Failed to load users:', err);
		} finally {
			loading = false;
		}
	}

	const debouncedSearch = debounce(() => loadUsers(), 300);

	function handleSearchInput() {
		debouncedSearch();
	}

	function handleTabChange() {
		loadUsers();
	}

	onMount(() => {
		loadUsers();
	});
</script>

<svelte:head>
	<title>İçerik Üreticilerini Keşfet | SadeceFanlar</title>
</svelte:head>

<div class="space-y-5">
	<h1 class="text-xl font-semibold text-neutral-900 dark:text-white">Keşfet</h1>

	<!-- Search -->
	<Input
		type="search"
		placeholder="İçerik üreticisi ara..."
		bind:value={searchQuery}
		on:input={handleSearchInput}
	/>

	<!-- Tabs -->
	<Tabs {tabs} bind:activeTab on:change={handleTabChange}>
		{#if loading}
			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				{#each Array(6) as _}
					<div class="bg-white dark:bg-neutral-900 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-800 overflow-hidden">
						<Skeleton variant="rectangular" height="96px" />
						<div class="p-4 pt-12">
							<Skeleton width="60%" />
							<Skeleton width="40%" class="mt-2" />
							<Skeleton lines={2} class="mt-4" />
						</div>
					</div>
				{/each}
			</div>
		{:else if users.length === 0}
			<div class="text-center py-12">
				<h2 class="text-lg font-medium text-neutral-900 dark:text-white mb-2">
					İçerik üreticisi bulunamadı
				</h2>
				<p class="text-neutral-500">
					{searchQuery ? 'Farklı bir arama terimi deneyin.' : 'Henüz içerik üreticisi yok.'}
				</p>
			</div>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				{#each users as user (user.id)}
					<UserCard
						{user}
						on:subscribe={(e) => (window.location.href = `/${e.detail.username}`)}
						on:message={(e) => (window.location.href = `/messages/${e.detail.id}`)}
					/>
				{/each}
			</div>
		{/if}
	</Tabs>
</div>
