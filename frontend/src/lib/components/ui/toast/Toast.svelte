<script lang="ts">
	import { cn } from '$lib/utils';
	import { createEventDispatcher, onMount } from 'svelte';
	import { fly } from 'svelte/transition';

	export let title: string;
	export let message: string;
	export let type: 'success' | 'error' | 'warning' | 'info' = 'info';
	export let duration = 5000;
	export let dismissible = true;
	let className = '';
	export { className as class };

	const dispatch = createEventDispatcher();

	const typeStyles: Record<string, { bg: string; icon: string; color: string }> = {
		success: {
			bg: 'bg-green-50 dark:bg-green-900/30 border-green-200 dark:border-green-800',
			icon: '✓',
			color: 'text-green-600 dark:text-green-400',
		},
		error: {
			bg: 'bg-red-50 dark:bg-red-900/30 border-red-200 dark:border-red-800',
			icon: '✕',
			color: 'text-red-600 dark:text-red-400',
		},
		warning: {
			bg: 'bg-yellow-50 dark:bg-yellow-900/30 border-yellow-200 dark:border-yellow-800',
			icon: '⚠',
			color: 'text-yellow-600 dark:text-yellow-400',
		},
		info: {
			bg: 'bg-blue-50 dark:bg-blue-900/30 border-blue-200 dark:border-blue-800',
			icon: 'ℹ',
			color: 'text-blue-600 dark:text-blue-400',
		},
	};

	let timeoutId: ReturnType<typeof setTimeout>;

	onMount(() => {
		if (duration > 0) {
			timeoutId = setTimeout(() => {
				dispatch('dismiss');
			}, duration);
		}

		return () => {
			if (timeoutId) clearTimeout(timeoutId);
		};
	});

	function handleDismiss() {
		dispatch('dismiss');
	}
</script>

<div
	class={cn(
		'pointer-events-auto w-full max-w-sm overflow-hidden rounded-lg border shadow-lg',
		typeStyles[type].bg,
		className
	)}
	transition:fly={{ y: -20, duration: 300 }}
	role="alert"
>
	<div class="p-4">
		<div class="flex items-start">
			<div class={cn('flex-shrink-0 text-lg', typeStyles[type].color)}>
				{typeStyles[type].icon}
			</div>
			<div class="ml-3 w-0 flex-1 pt-0.5">
				<p class={cn('text-sm font-medium', typeStyles[type].color)}>{title}</p>
				<p class="mt-1 text-sm text-neutral-600 dark:text-neutral-400">{message}</p>
			</div>
			{#if dismissible}
				<div class="ml-4 flex flex-shrink-0">
					<button
						type="button"
						class="inline-flex rounded-md text-neutral-400 hover:text-neutral-500 focus:outline-none focus:ring-2 focus:ring-primary"
						on:click={handleDismiss}
					>
						<span class="sr-only">Close</span>
						<svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
							<path
								fill-rule="evenodd"
								d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
								clip-rule="evenodd"
							/>
						</svg>
					</button>
				</div>
			{/if}
		</div>
	</div>
</div>
