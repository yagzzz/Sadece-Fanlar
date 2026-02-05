<script lang="ts">
	import { cn } from '$lib/utils';

	export let type:
		| 'text'
		| 'email'
		| 'password'
		| 'number'
		| 'tel'
		| 'url'
		| 'search'
		| 'date'
		| 'datetime-local' = 'text';
	export let value = '';
	export let placeholder = '';
	export let disabled = false;
	export let error = '';
	export let label = '';
	let className = '';
	export { className as class };
	const inputId = `input-${Math.random().toString(36).slice(2, 10)}`;

	function handleInput(event: Event) {
		value = (event.currentTarget as HTMLInputElement).value;
	}
</script>

<div class="w-full">
	{#if label}
		<label for={inputId} class="mb-1.5 block text-sm font-medium text-foreground">
			{label}
		</label>
	{/if}
	<input
		id={inputId}
		type={type}
		value={value}
		on:input={handleInput}
		{placeholder}
		{disabled}
		class={cn(
			'flex h-10 w-full rounded-lg border bg-background px-3 py-2 text-sm',
			'ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium',
			'placeholder:text-muted-foreground',
			'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
			'disabled:cursor-not-allowed disabled:opacity-50',
			error ? 'border-destructive' : 'border-input',
			className
		)}
		{...$$restProps}
	/>
	{#if error}
		<p class="mt-1 text-sm text-destructive">{error}</p>
	{/if}
</div>
