<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { authStore, checkAuth } from '$lib/stores/auth';
	import { Toast } from '$lib/components/ui';
	import { writable } from 'svelte/store';

	// Toast store
	export const toasts = writable<Array<{
		id: string;
		title: string;
		message: string;
		type: 'success' | 'error' | 'warning' | 'info';
	}>>([]);

	onMount(() => {
		checkAuth();
	});

	function removeToast(id: string) {
		toasts.update((t) => t.filter((toast) => toast.id !== id));
	}
</script>

<svelte:head>
	<title>SadeceFanlar</title>
	<meta name="description" content="Anonim içerik üretici platformu" />
</svelte:head>

{#if $authStore.initialized}
	<slot />
{:else}
	<div class="min-h-screen flex items-center justify-center bg-white dark:bg-neutral-950">
		<div class="h-8 w-8 rounded-full border-2 border-neutral-300 border-t-neutral-800 animate-spin"></div>
	</div>
{/if}

<!-- Toast Container -->
<div class="fixed top-4 right-4 z-50 space-y-2 pointer-events-none">
	{#each $toasts as toast (toast.id)}
		<Toast
			title={toast.title}
			message={toast.message}
			type={toast.type}
			on:dismiss={() => removeToast(toast.id)}
		/>
	{/each}
</div>
