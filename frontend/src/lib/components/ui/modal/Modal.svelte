<script lang="ts">
	import { cn } from '$lib/utils';
	import { fade, scale } from 'svelte/transition';

	export let open = false;
	export let title = '';
	export let description = '';
	let className = '';
	export { className as class };

	function handleBackdropClick(event: MouseEvent) {
		if (event.target === event.currentTarget) {
			open = false;
		}
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Escape') {
			open = false;
		}
	}
</script>

<svelte:window on:keydown={handleKeydown} />

{#if open}
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<div
		class="fixed inset-0 z-50 flex items-center justify-center"
		transition:fade={{ duration: 150 }}
		role="dialog"
		aria-modal="true"
	>
		<!-- Backdrop -->
		<div
			class="fixed inset-0 bg-black/50 backdrop-blur-sm"
			role="button"
			aria-label="Close modal"
			tabindex="0"
			on:click={handleBackdropClick}
			on:keydown={handleKeydown}
		/>

		<!-- Modal -->
		<div
			class={cn(
				'relative z-50 mx-4 w-full max-w-lg rounded-xl bg-card p-6 shadow-lg',
				className
			)}
			transition:scale={{ duration: 150, start: 0.95 }}
		>
			<!-- Close button -->
			<button
				on:click={() => (open = false)}
				class="absolute right-4 top-4 rounded-lg p-1 text-muted-foreground hover:bg-muted hover:text-foreground"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					width="20"
					height="20"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
				>
					<path d="M18 6 6 18" />
					<path d="m6 6 12 12" />
				</svg>
			</button>

			<!-- Header -->
			{#if title || description}
				<div class="mb-4">
					{#if title}
						<h2 class="text-lg font-semibold">{title}</h2>
					{/if}
					{#if description}
						<p class="mt-1 text-sm text-muted-foreground">{description}</p>
					{/if}
				</div>
			{/if}

			<!-- Content -->
			<slot />
		</div>
	</div>
{/if}
