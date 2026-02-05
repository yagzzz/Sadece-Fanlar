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

	onMount(async () => {
		await checkAuth();
	});

	function removeToast(id: string) {
		toasts.update((t) => t.filter((toast) => toast.id !== id));
	}
</script>

<svelte:head>
	<title>SadeceFanlar - Anonymous Creator Platform</title>
	<meta name="description" content="Support your favorite creators anonymously with cryptocurrency payments. Privacy-first content platform." />
</svelte:head>

<div class="min-h-screen bg-neutral-50 dark:bg-neutral-950">
	<slot />
</div>

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
