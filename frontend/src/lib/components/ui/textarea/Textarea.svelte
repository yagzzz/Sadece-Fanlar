<script lang="ts">
	import { cn } from '$lib/utils';

	export let value = '';
	export let placeholder = '';
	export let label = '';
	export let error = '';
	export let disabled = false;
	export let rows = 4;
	export let maxLength: number | undefined = undefined;
	let className = '';
	export { className as class };

	let showCount = !!maxLength;
	const textareaId = `textarea-${Math.random().toString(36).slice(2, 10)}`;
</script>

<div class={cn('w-full', className)}>
	{#if label}
		<label for={textareaId} class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
			{label}
		</label>
	{/if}

	<div class="relative">
		<textarea
			id={textareaId}
			bind:value
			{placeholder}
			{disabled}
			{rows}
			maxlength={maxLength}
			class={cn(
				'block w-full rounded-lg border px-3 py-2 text-sm transition-colors resize-none',
				'bg-white dark:bg-neutral-900',
				'placeholder:text-neutral-400 dark:placeholder:text-neutral-500',
				'focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
				error
					? 'border-red-500 focus:ring-red-500'
					: 'border-neutral-300 dark:border-neutral-600',
				disabled && 'opacity-50 cursor-not-allowed bg-neutral-100 dark:bg-neutral-800'
			)}
		/>

		{#if showCount}
			<div class="absolute bottom-2 right-2 text-xs text-neutral-400">
				{value.length}{maxLength ? `/${maxLength}` : ''}
			</div>
		{/if}
	</div>

	{#if error}
		<p class="mt-1 text-sm text-red-500">{error}</p>
	{/if}
</div>
