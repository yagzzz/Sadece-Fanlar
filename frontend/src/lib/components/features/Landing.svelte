<script lang="ts">
	import { Button } from '$lib/components/ui';
</script>

<div class="max-w-2xl mx-auto px-4 py-16 sm:py-24">
	<section class="text-center mb-16">
		<h1 class="text-3xl sm:text-4xl font-semibold tracking-tight text-neutral-900 dark:text-white mb-4">
			İçerik üreticileri için anonim abonelik platformu
		</h1>
		<p class="text-neutral-600 dark:text-neutral-400 text-lg mb-8 max-w-xl mx-auto">
			E-posta veya kimlik gerekmez. Ödemeler yalnızca kripto ile yapılır.
		</p>
		<div class="flex flex-col sm:flex-row gap-3 justify-center">
			<Button href="/register" size="lg">Hesap oluştur</Button>
			<Button href="/login" variant="outline" size="lg">Giriş yap</Button>
		</div>
	</section>

	<section class="grid sm:grid-cols-3 gap-6 mb-16 text-sm">
		<div class="border border-neutral-200 dark:border-neutral-800 rounded-lg p-5">
			<p class="font-medium mb-2">Anonim kayıt</p>
			<p class="text-neutral-500">Kullanıcı adı ve şifre yeterli. E-posta isteğe bağlı.</p>
		</div>
		<div class="border border-neutral-200 dark:border-neutral-800 rounded-lg p-5">
			<p class="font-medium mb-2">Kripto ödeme</p>
			<p class="text-neutral-500">Monero ve Bitcoin. Kart veya banka bilgisi yok.</p>
		</div>
		<div class="border border-neutral-200 dark:border-neutral-800 rounded-lg p-5">
			<p class="font-medium mb-2">Üretici odaklı</p>
			<p class="text-neutral-500">Abonelik, bahşiş ve kilitli içerik ile kazan.</p>
		</div>
	</section>

	<section class="border-t border-neutral-200 dark:border-neutral-800 pt-10 text-center text-sm text-neutral-500">
		<p class="mb-3">18 yaş ve üzeri içindir. Yasadışı içerik yasaktır.</p>
		<div class="flex justify-center gap-4">
			<a href="/terms" class="hover:text-neutral-800 dark:hover:text-neutral-300">Kullanım Şartları</a>
			<a href="/privacy" class="hover:text-neutral-800 dark:hover:text-neutral-300">Gizlilik</a>
		</div>
	</section>
</div>
