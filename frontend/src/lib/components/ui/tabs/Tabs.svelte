<script lang="ts">
	import { cn } from '$lib/utils';
	import { createEventDispatcher } from 'svelte';

	type Tab = {
		id: string;
		label: string;
		icon?: string;
		disabled?: boolean;
	};

	export let tabs: Tab[];
	export let activeTab: string;
	let className = '';
	export { className as class };

	const dispatch = createEventDispatcher();

	function handleSelect(tab: Tab) {
		if (tab.disabled) return;
		activeTab = tab.id;
		dispatch('change', tab.id);
	}
</script>

<div class={cn('border-b border-neutral-200 dark:border-neutral-700', className)}>
	<nav class="-mb-px flex space-x-8" aria-label="Tabs">
		{#each tabs as tab}
			<button
				type="button"
				class={cn(
					'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors',
					activeTab === tab.id
						? 'border-primary text-primary'
						: 'border-transparent text-neutral-500 hover:text-neutral-700 hover:border-neutral-300 dark:text-neutral-400 dark:hover:text-neutral-300',
					tab.disabled && 'opacity-50 cursor-not-allowed'
				)}
				on:click={() => handleSelect(tab)}
				disabled={tab.disabled}
				aria-selected={activeTab === tab.id}
				role="tab"
			>
				{#if tab.icon}
					<span class="mr-2">{tab.icon}</span>
				{/if}
				{tab.label}
			</button>
		{/each}
	</nav>
</div>

<div class="mt-4">
	<slot />
</div>
