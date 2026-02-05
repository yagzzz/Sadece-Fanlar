<script lang="ts">
	import { cn } from '$lib/utils';

	export let src: string | undefined = undefined;
	export let alt = '';
	export let fallback = '';
	export let size: 'sm' | 'md' | 'lg' | 'xl' = 'md';
	let className = '';
	export { className as class };

	const sizes: Record<string, string> = {
		sm: 'h-8 w-8',
		md: 'h-10 w-10',
		lg: 'h-16 w-16',
		xl: 'h-24 w-24',
	};

	let imageError = false;

	function handleError() {
		imageError = true;
	}

	$: initials = fallback || alt?.charAt(0)?.toUpperCase() || '?';
</script>

<div
	class={cn(
		'relative flex shrink-0 overflow-hidden rounded-full bg-muted',
		sizes[size],
		className
	)}
>
	{#if src && !imageError}
		<img {src} {alt} on:error={handleError} class="aspect-square h-full w-full object-cover" />
	{:else}
		<span
			class="flex h-full w-full items-center justify-center bg-gradient-to-br from-primary to-accent text-sm font-medium text-white"
		>
			{initials}
		</span>
	{/if}
</div>
