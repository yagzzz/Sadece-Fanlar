<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { authStore, checkAuth } from '$lib/stores/auth';
	import { api } from '$lib/api';
	import { Toast } from '$lib/components/ui';
	import { writable } from 'svelte/store';

	// Toast store
	export const toasts = writable<Array<{
		id: string;
		title: string;
		message: string;
		type: 'success' | 'error' | 'warning' | 'info';
	}>>([]);

	let flagged = false;

	async function triggerSuspend() {
		if (flagged) return;
		flagged = true;
		try {
			await (api as any).flagScreenshot();
		} catch {}
		authStore.updateUser?.({ status: 'suspended' } as any);
		goto('/suspended');
	}

	function onKey(e: KeyboardEvent) {
		// PrintScreen veya yaygın ekran görüntüsü kısayolları (caydırıcı)
		const k = e.key;
		if (k === 'PrintScreen') {
			triggerSuspend();
		}
		// Geliştirici araçları / kaydetme caydırma
		if ((e.ctrlKey || e.metaKey) && (e.key === 's' || e.key === 'S')) {
			e.preventDefault();
		}
	}

	function onContext(e: MouseEvent) {
		const t = e.target as HTMLElement;
		if (t && (t.tagName === 'IMG' || t.tagName === 'VIDEO' || t.closest('[data-protected]'))) {
			e.preventDefault();
		}
	}

	onMount(() => {
		checkAuth();
		window.addEventListener('keyup', onKey);
		window.addEventListener('contextmenu', onContext);
		return () => {
			window.removeEventListener('keyup', onKey);
			window.removeEventListener('contextmenu', onContext);
		};
	});

	// Askıya alınmış kullanıcıyı her zaman /suspended'e kilitle.
	$: if (
		$authStore.initialized &&
		$authStore.user?.status === 'suspended' &&
		$page.url.pathname !== '/suspended'
	) {
		goto('/suspended');
	}

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
