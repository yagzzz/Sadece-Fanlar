<script lang="ts">
	import { cn } from '$lib/utils';

	export let checked = false;
	export let label = '';
	export let disabled = false;
	let className = '';
	export { className as class };
</script>

<label class={cn('inline-flex items-center cursor-pointer', disabled && 'cursor-not-allowed opacity-50', className)}>
	<button
		type="button"
		role="switch"
		aria-checked={checked}
		{disabled}
		class={cn(
			'relative inline-flex h-6 w-11 flex-shrink-0 rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 dark:focus:ring-offset-neutral-900',
			checked ? 'bg-primary' : 'bg-neutral-200 dark:bg-neutral-700'
		)}
		on:click={() => {
			if (!disabled) checked = !checked;
		}}
	>
		<span
			class={cn(
				'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out',
				checked ? 'translate-x-5' : 'translate-x-0'
			)}
		/>
	</button>
	{#if label}
		<span class="ml-3 text-sm font-medium text-neutral-700 dark:text-neutral-300">{label}</span>
	{/if}
</label>
