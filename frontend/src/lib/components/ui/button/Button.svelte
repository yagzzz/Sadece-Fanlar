<script lang="ts">
	import { cn } from '$lib/utils';

	type Variant = 'default' | 'secondary' | 'outline' | 'ghost' | 'danger';
	type Size = 'sm' | 'md' | 'lg' | 'icon';

	export let variant: Variant = 'default';
	export let size: Size = 'md';
	export let disabled = false;
	export let loading = false;
	export let type: 'button' | 'submit' | 'reset' = 'button';
	export let href: string | undefined = undefined;
	let className = '';
	export { className as class };

	const variants: Record<Variant, string> = {
		default: 'bg-primary text-white hover:bg-primary/90',
		secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
		outline: 'border border-input bg-transparent hover:bg-accent hover:text-accent-foreground',
		ghost: 'hover:bg-accent hover:text-accent-foreground',
		danger: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
	};

	const sizes: Record<Size, string> = {
		sm: 'h-8 px-3 text-xs',
		md: 'h-10 px-4 py-2',
		lg: 'h-12 px-6 text-lg',
		icon: 'h-10 w-10',
	};
</script>

{#if href && !disabled}
	<a
		{href}
		class={cn(
			'inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors',
			'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
			variants[variant],
			sizes[size],
			className
		)}
		on:click
		{...$$restProps}
	>
		<slot />
	</a>
{:else}
	<button
		{type}
		disabled={disabled || loading}
		class={cn(
			'inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors',
			'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
			'disabled:pointer-events-none disabled:opacity-50',
			variants[variant],
			sizes[size],
			className
		)}
		on:click
		{...$$restProps}
	>
		{#if loading}
			<svg
				class="h-4 w-4 animate-spin"
				xmlns="http://www.w3.org/2000/svg"
				fill="none"
				viewBox="0 0 24 24"
			>
				<circle
					class="opacity-25"
					cx="12"
					cy="12"
					r="10"
					stroke="currentColor"
					stroke-width="4"
				/>
				<path
					class="opacity-75"
					fill="currentColor"
					d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
				/>
			</svg>
		{/if}
		<slot />
	</button>
{/if}
