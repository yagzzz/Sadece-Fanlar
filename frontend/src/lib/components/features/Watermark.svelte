<script lang="ts">
	import { authStore } from '$lib/stores/auth';
	// Medya üzerinde görünmez-zayıf, tekrarlanan filigran: sızan görüntü
	// hangi kullanıcıya ait, izlenebilir olur.
	$: label = $authStore.user ? `@${$authStore.user.username}` : '';
</script>

{#if label}
	<div class="pointer-events-none absolute inset-0 z-20 overflow-hidden select-none" aria-hidden="true">
		<div class="absolute inset-0 flex flex-wrap content-around justify-around opacity-[0.07] rotate-[-25deg] scale-125">
			{#each Array(18) as _, i}
				<span class="text-white text-xs whitespace-nowrap px-6 py-3">{label}</span>
			{/each}
		</div>
	</div>
{/if}
