<script lang="ts">
	import { cn } from '$lib/utils';

	export let variant: 'text' | 'circular' | 'rectangular' = 'text';
	export let width: string | undefined = undefined;
	export let height: string | undefined = undefined;
	export let lines: number = 1;
	let className = '';
	export { className as class };

	const baseClass = 'animate-pulse bg-neutral-200 dark:bg-neutral-700 rounded';
</script>

{#if variant === 'circular'}
	<div
		class={cn(baseClass, 'rounded-full', className)}
		style:width={width || '40px'}
		style:height={height || '40px'}
	/>
{:else if variant === 'rectangular'}
	<div
		class={cn(baseClass, className)}
		style:width={width || '100%'}
		style:height={height || '100px'}
	/>
{:else}
	<div class={cn('space-y-2', className)}>
		{#each Array(lines) as _, i}
			<div
				class={cn(baseClass, 'h-4')}
				style:width={i === lines - 1 && lines > 1 ? '60%' : width || '100%'}
			/>
		{/each}
	</div>
{/if}
