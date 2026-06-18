<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';

	export let position: string;
	export let vertical = false;
	let className = '';
	export { className as class };

	let ads: any[] = [];

	onMount(async () => {
		ads = await (api as any).ads.list(position);
	});

	function handleClick(ad: any) {
		(api as any).ads.click(ad.id).catch(() => {});
		if (ad.link_url) window.open(ad.link_url, '_blank', 'noopener');
	}
</script>

{#if ads.length > 0}
	<div class={className}>
		{#each ads as ad (ad.id)}
			<div
				class="relative overflow-hidden rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 cursor-pointer {vertical ? 'mb-4' : 'mb-4'}"
				on:click={() => handleClick(ad)}
				on:keydown={(e) => e.key === 'Enter' && handleClick(ad)}
				role="button"
				tabindex="0"
			>
				<!-- "Reklam" etiketi (sarı, fark edilir) -->
				<span class="absolute top-2 right-2 z-10 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide rounded bg-yellow-400 text-black shadow">
					Reklam
				</span>

				{#if ad.content_html}
					{@html ad.content_html}
				{:else if ad.image_url && (ad.image_url.endsWith('.mp4') || ad.image_url.endsWith('.webm'))}
					<video src={ad.image_url} autoplay muted loop playsinline class="w-full {vertical ? 'h-96 object-cover' : 'h-auto'}"></video>
				{:else if ad.image_url}
					<img src={ad.image_url} alt={ad.name} class="w-full {vertical ? 'h-96 object-cover' : 'h-auto'}" />
				{:else}
					<div class="p-6 text-center text-sm text-neutral-500">{ad.name}</div>
				{/if}
			</div>
		{/each}
	</div>
{/if}
