<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';

	// Geriye dönük uyum: hem position hem placement kabul et
	export let position: string = '';
	export let placement: string = '';
	export let vertical = false;
	let className = '';
	export { className as class };

	$: slot = placement || position;

	let ads: any[] = [];

	onMount(async () => {
		if (!slot) return;
		ads = await (api as any).ads.list(slot);
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
				class="relative overflow-hidden rounded-xl border border-border bg-card {ad.link_url ? 'cursor-pointer' : ''} mb-4"
				on:click={() => ad.link_url && handleClick(ad)}
				on:keydown={(e) => e.key === 'Enter' && ad.link_url && handleClick(ad)}
				role="button"
				tabindex="0"
			>
				<!-- "Reklam" etiketi (sarı, fark edilir) -->
				<span class="absolute top-2 right-2 z-10 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide rounded bg-yellow-400 text-black shadow">
					Reklam
				</span>

				{#if ad.ad_type === 'video' && ad.media_url}
					<video src={ad.media_url} autoplay muted loop playsinline class="w-full {vertical ? 'h-96 object-cover' : 'h-auto'}"></video>
				{:else if ad.ad_type === 'image' && ad.media_url}
					<img src={ad.media_url} alt={ad.title} class="w-full {vertical ? 'h-96 object-cover' : 'h-auto'}" />
				{:else if ad.ad_type === 'text'}
					<div class="p-5">
						<p class="font-semibold text-sm mb-1">{ad.title}</p>
						{#if ad.text_content}<p class="text-sm text-muted-foreground">{ad.text_content}</p>{/if}
						{#if ad.link_url}<p class="text-xs text-primary mt-2">Daha fazla →</p>{/if}
					</div>
				{:else}
					<div class="p-6 text-center text-sm text-muted-foreground">{ad.title}</div>
				{/if}
			</div>
		{/each}
	</div>
{/if}
