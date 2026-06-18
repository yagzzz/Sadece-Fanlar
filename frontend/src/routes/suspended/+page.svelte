<script lang="ts">
	import { authStore, logout } from '$lib/stores/auth';
	$: user = $authStore.user;
</script>

<svelte:head>
	<title>Hesap Askıya Alındı</title>
	<meta name="robots" content="noindex, nofollow" />
</svelte:head>

<div class="min-h-screen flex items-center justify-center bg-gradient-to-b from-red-950 via-neutral-950 to-black px-6 text-center">
	<div class="max-w-lg">
		<div class="text-7xl mb-6">🚫</div>
		<h1 class="text-3xl sm:text-4xl font-extrabold text-red-500 mb-4">
			Hesabınız Askıya Alındı
		</h1>
		<p class="text-neutral-300 text-lg mb-6 leading-relaxed">
			Sistemimiz hesabınızda <strong class="text-red-400">izinsiz ekran görüntüsü / kayıt girişimi</strong>
			tespit etti. İçerik üreticilerinin emeğini çalmaya çalışmak bu platformda
			<strong class="text-white"> en ağır ihlaldir.</strong>
		</p>
		<div class="bg-black/40 border border-red-900 rounded-xl p-5 mb-6 text-left">
			<p class="text-neutral-400 text-sm mb-2">⚠️ Bilmeniz gerekenler:</p>
			<ul class="text-neutral-300 text-sm space-y-1 list-disc list-inside">
				<li>Tüm içeriklerde kimliğinize özel görünmez filigran bulunur.</li>
				<li>Sızdırılan her görüntü doğrudan sizinle ilişkilendirilebilir.</li>
				<li>Bakiyeniz ve erişiminiz donduruldu.</li>
			</ul>
		</div>
		<p class="text-neutral-500 text-sm mb-8">
			Bunun bir hata olduğunu düşünüyorsanız destek ekibine yazın. O zamana kadar
			bu sayfa dışındaki hiçbir alana erişemezsiniz.
		</p>
		<button
			class="px-6 py-3 rounded-lg bg-neutral-800 text-neutral-200 hover:bg-neutral-700 transition-colors"
			on:click={() => { logout(); window.location.href = '/'; }}
		>
			Çıkış yap
		</button>
	</div>
</div>
