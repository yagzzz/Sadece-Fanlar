<script lang="ts">
	import { cn } from '$lib/utils';

	type Variant = 'default' | 'primary' | 'success' | 'warning' | 'error' | 'outline';

	export let variant: Variant = 'default';
	let className = '';
	export { className as class };

	const variants: Record<Variant, string> = {
		default: 'bg-secondary text-secondary-foreground',
		primary: 'bg-primary/10 text-primary',
		success: 'bg-green-500/10 text-green-500',
		warning: 'bg-yellow-500/10 text-yellow-500',
		error: 'bg-red-500/10 text-red-500',
		outline: 'border border-input bg-transparent',
	};
</script>

<span
	class={cn(
		'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors',
		variants[variant],
		className
	)}
>
	<slot />
</span>
