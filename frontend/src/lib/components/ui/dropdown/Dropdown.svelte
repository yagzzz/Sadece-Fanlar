<script lang="ts">
	import { cn } from '$lib/utils';
	import { clickOutside } from '$lib/utils';
	import { slide } from 'svelte/transition';

	type DropdownItem = {
		id: string;
		label: string;
		icon?: string;
		disabled?: boolean;
		danger?: boolean;
		divider?: boolean;
	};

	export let items: DropdownItem[];
	export let align: 'left' | 'right' = 'right';
	let className = '';
	export { className as class };

	let isOpen = false;

	import { createEventDispatcher } from 'svelte';
	const dispatch = createEventDispatcher();

	function handleSelect(item: DropdownItem) {
		if (item.disabled || item.divider) return;
		dispatch('select', item.id);
		isOpen = false;
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') {
			isOpen = false;
		}
	}
</script>

<svelte:window on:keydown={handleKeydown} />

<div class={cn('relative inline-block text-left', className)} use:clickOutside={() => (isOpen = false)}>
	<div on:click={() => (isOpen = !isOpen)} on:keydown={() => {}} role="button" tabindex="0">
		<slot name="trigger">
			<button
				type="button"
				class="inline-flex items-center justify-center p-2 rounded-md text-neutral-400 hover:text-neutral-500 hover:bg-neutral-100 dark:hover:bg-neutral-800"
			>
				<svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
					<path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
				</svg>
			</button>
		</slot>
	</div>

	{#if isOpen}
		<div
			class={cn(
				'absolute z-50 mt-2 w-56 rounded-md shadow-lg bg-white dark:bg-neutral-800 ring-1 ring-black ring-opacity-5 focus:outline-none',
				align === 'right' ? 'right-0 origin-top-right' : 'left-0 origin-top-left'
			)}
			transition:slide={{ duration: 150 }}
			role="menu"
			aria-orientation="vertical"
		>
			<div class="py-1" role="none">
				{#each items as item}
					{#if item.divider}
						<div class="border-t border-neutral-200 dark:border-neutral-700 my-1" />
					{:else}
						<button
							type="button"
							class={cn(
								'w-full text-left px-4 py-2 text-sm transition-colors',
								item.danger
									? 'text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20'
									: 'text-neutral-700 dark:text-neutral-200 hover:bg-neutral-100 dark:hover:bg-neutral-700',
								item.disabled && 'opacity-50 cursor-not-allowed'
							)}
							on:click={() => handleSelect(item)}
							disabled={item.disabled}
							role="menuitem"
						>
							{#if item.icon}
								<span class="mr-2">{item.icon}</span>
							{/if}
							{item.label}
						</button>
					{/if}
				{/each}
			</div>
		</div>
	{/if}
</div>
