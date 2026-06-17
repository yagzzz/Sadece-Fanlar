<script lang="ts">
	import { Button } from '$lib/components/ui';

	const trustChips = [
		{ icon: '🔒', label: 'Anonim hesap' },
		{ icon: '🪙', label: 'Sadece kripto ödeme' },
		{ icon: '🚫', label: 'Kişisel veri yok' },
		{ icon: '🔞', label: 'Sadece 18+' },
	];

	const steps = [
		{
			n: '1',
			title: 'Anonim kayıt ol',
			desc: 'E-posta veya kimlik gerekmez. Sadece bir kullanıcı adı ve şifre yeterli.',
		},
		{
			n: '2',
			title: 'Kripto ile bakiye yükle',
			desc: 'Monero (XMR) veya Bitcoin (BTC) ile öde. Banka veya kart bilgisi istenmez.',
		},
		{
			n: '3',
			title: 'Keşfet, abone ol, destekle',
			desc: 'Beğendiğin üreticilere abone ol, içerik kilidini aç, bahşiş gönder.',
		},
	];

	const features = [
		{
			icon: '🕶️',
			title: 'Gerçek anonimlik',
			desc: 'E-posta zorunlu değil. IP adresleri loglanmaz. Profilin arama motorlarında indekslenmez.',
		},
		{
			icon: '🪙',
			title: 'Sadece kripto',
			desc: 'Monero ve Bitcoin. Self-hosted ödeme altyapısı; üçüncü taraf ödeme sağlayıcısı yok.',
		},
		{
			icon: '🛡️',
			title: 'Güçlü güvenlik',
			desc: '2FA (TOTP), şifrelenmiş parolalar, oran sınırlama ve modern güvenlik başlıkları.',
		},
		{
			icon: '💸',
			title: 'Üreticiye yüksek pay',
			desc: 'Kazancını dilediğin zaman kripto olarak çek. Şeffaf, düşük komisyon.',
		},
		{
			icon: '🇹🇷',
			title: 'Türkçe ve yerel',
			desc: 'Baştan sona Türkçe arayüz, Türkiye’deki üreticiler ve hayranlar için tasarlandı.',
		},
		{
			icon: '⚖️',
			title: 'Yasalara saygılı',
			desc: 'Yalnızca 18+ yetişkinler. Yasa dışı içeriğe sıfır tolerans, kolay raporlama.',
		},
	];

	const faqs = [
		{
			q: 'Gerçekten anonim mi?',
			a: 'Evet. Kayıt için e-posta veya kimlik istemiyoruz; e-posta tamamen isteğe bağlıdır. Sunucularımız ziyaretçi IP’lerini erişim loglarında saklamaz.',
		},
		{
			q: 'Hangi ödeme yöntemleri var?',
			a: 'Yalnızca kripto: Monero (XMR) ve Bitcoin (BTC). Kredi kartı veya banka bilgisi istenmez, saklanmaz.',
		},
		{
			q: 'Kazancımı nasıl çekerim?',
			a: 'İçerik üreticileri kazançlarını istedikleri kripto cüzdan adresine çekebilir. Çekim talepleri kısa sürede işlenir.',
		},
		{
			q: 'Yaş ve içerik kuralları neler?',
			a: 'Platform yalnızca 18 yaşından büyükler içindir. Reşit olmayanları içeren veya yasa dışı her türlü içerik kesinlikle yasaktır ve anında kaldırılır.',
		},
	];

	let openFaq: number | null = 0;
	function toggleFaq(i: number) {
		openFaq = openFaq === i ? null : i;
	}
</script>

<div class="px-4 sm:px-6 pb-16">
	<!-- Hero -->
	<section class="relative overflow-hidden rounded-3xl border border-neutral-200 dark:border-neutral-800 bg-gradient-to-br from-primary-50 via-white to-white dark:from-neutral-900 dark:via-neutral-950 dark:to-neutral-950 px-6 py-14 sm:py-20 text-center">
		<div class="pointer-events-none absolute -top-24 -right-24 h-72 w-72 rounded-full bg-primary-400/20 blur-3xl" />
		<div class="pointer-events-none absolute -bottom-24 -left-24 h-72 w-72 rounded-full bg-fuchsia-500/10 blur-3xl" />

		<div class="relative mx-auto max-w-3xl">
			<span class="inline-flex items-center gap-2 rounded-full border border-primary-200 dark:border-primary-900 bg-white/70 dark:bg-neutral-900/70 px-4 py-1.5 text-xs font-medium text-primary-700 dark:text-primary-300">
				🔒 Gizlilik öncelikli · Sadece kripto · Türkiye
			</span>

			<h1 class="mt-6 text-4xl sm:text-5xl font-extrabold tracking-tight text-neutral-900 dark:text-white">
				İçeriğini özgürce paylaş,
				<span class="text-primary">anonim kal</span>.
			</h1>

			<p class="mx-auto mt-5 max-w-2xl text-lg text-neutral-600 dark:text-neutral-300">
				SadeceFanlar, içerik üreticileri ve hayranları anonim olarak buluşturan,
				yalnızca kripto para ile çalışan abonelik platformudur. Kişisel veri yok,
				banka yok, takip yok.
			</p>

			<div class="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3">
				<Button href="/register" size="lg" class="w-full sm:w-auto shadow-glow">
					Ücretsiz ve anonim kayıt ol
				</Button>
				<Button href="/explore" size="lg" variant="outline" class="w-full sm:w-auto">
					Üreticileri keşfet
				</Button>
			</div>

			<div class="mt-8 flex flex-wrap items-center justify-center gap-2">
				{#each trustChips as chip}
					<span class="inline-flex items-center gap-1.5 rounded-full bg-neutral-100 dark:bg-neutral-800/80 px-3 py-1.5 text-sm text-neutral-700 dark:text-neutral-200">
						<span>{chip.icon}</span>{chip.label}
					</span>
				{/each}
			</div>
		</div>
	</section>

	<!-- How it works -->
	<section class="mx-auto mt-16 max-w-5xl">
		<h2 class="text-center text-2xl sm:text-3xl font-bold text-neutral-900 dark:text-white">
			Nasıl çalışır?
		</h2>
		<p class="mt-2 text-center text-neutral-500">Üç basit adımda başla.</p>

		<div class="mt-10 grid gap-6 sm:grid-cols-3">
			{#each steps as step}
				<div class="rounded-2xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 p-6">
					<div class="flex h-11 w-11 items-center justify-center rounded-full bg-primary text-white font-bold">
						{step.n}
					</div>
					<h3 class="mt-4 text-lg font-semibold text-neutral-900 dark:text-white">{step.title}</h3>
					<p class="mt-2 text-sm text-neutral-600 dark:text-neutral-400">{step.desc}</p>
				</div>
			{/each}
		</div>
	</section>

	<!-- Features -->
	<section class="mx-auto mt-16 max-w-5xl">
		<h2 class="text-center text-2xl sm:text-3xl font-bold text-neutral-900 dark:text-white">
			Neden SadeceFanlar?
		</h2>
		<div class="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
			{#each features as f}
				<div class="rounded-2xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 p-6">
					<div class="text-3xl">{f.icon}</div>
					<h3 class="mt-3 text-lg font-semibold text-neutral-900 dark:text-white">{f.title}</h3>
					<p class="mt-2 text-sm text-neutral-600 dark:text-neutral-400">{f.desc}</p>
				</div>
			{/each}
		</div>
	</section>

	<!-- Creator CTA -->
	<section class="mx-auto mt-16 max-w-5xl">
		<div class="rounded-3xl bg-neutral-900 dark:bg-neutral-900 border border-neutral-800 px-6 py-12 text-center">
			<h2 class="text-2xl sm:text-3xl font-bold text-white">İçerik üreticisi misin?</h2>
			<p class="mx-auto mt-3 max-w-2xl text-neutral-300">
				Takma adınla kazanmaya başla. Gerçek isim, kimlik belgesi veya yüz fotoğrafı
				istemiyoruz — yalnızca 18 yaşından büyük olduğunu onaylaman yeterli.
			</p>
			<div class="mt-7 flex flex-col sm:flex-row items-center justify-center gap-3">
				<Button href="/register" size="lg" class="w-full sm:w-auto">Üretici olarak başla</Button>
				<Button href="/explore" size="lg" variant="outline" class="w-full sm:w-auto border-neutral-600 text-white hover:bg-neutral-800">
					Önce keşfet
				</Button>
			</div>
		</div>
	</section>

	<!-- FAQ -->
	<section class="mx-auto mt-16 max-w-3xl">
		<h2 class="text-center text-2xl sm:text-3xl font-bold text-neutral-900 dark:text-white">
			Sıkça sorulan sorular
		</h2>
		<div class="mt-8 space-y-3">
			{#each faqs as faq, i}
				<div class="rounded-2xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900">
					<button
						type="button"
						class="flex w-full items-center justify-between gap-4 px-5 py-4 text-left"
						on:click={() => toggleFaq(i)}
						aria-expanded={openFaq === i}
					>
						<span class="font-medium text-neutral-900 dark:text-white">{faq.q}</span>
						<span class="text-primary text-xl leading-none">{openFaq === i ? '−' : '+'}</span>
					</button>
					{#if openFaq === i}
						<p class="px-5 pb-5 -mt-1 text-sm text-neutral-600 dark:text-neutral-400">{faq.a}</p>
					{/if}
				</div>
			{/each}
		</div>
	</section>

	<!-- 18+ / Legal notice -->
	<section class="mx-auto mt-14 max-w-3xl">
		<div class="rounded-2xl border border-amber-200 dark:border-amber-900/50 bg-amber-50 dark:bg-amber-900/10 p-5 text-center">
			<p class="text-sm text-amber-800 dark:text-amber-300">
				🔞 Bu platform yalnızca <strong>18 yaş ve üzeri</strong> yetişkinler içindir.
				Reşit olmayan kişileri içeren veya yasa dışı her türlü içerik kesinlikle yasaktır.
			</p>
		</div>
	</section>

	<!-- Footer -->
	<footer class="mx-auto mt-12 max-w-5xl border-t border-neutral-200 dark:border-neutral-800 pt-8">
		<div class="flex flex-col items-center gap-4 sm:flex-row sm:justify-between">
			<div class="text-center sm:text-left">
				<div class="text-lg font-bold text-primary">SadeceFanlar</div>
				<p class="mt-1 text-xs text-neutral-500">Gizliliğinize saygı duyan içerik platformu.</p>
			</div>
			<nav class="flex flex-wrap items-center justify-center gap-x-5 gap-y-2 text-sm text-neutral-500">
				<a href="/explore" class="hover:text-primary">Keşfet</a>
				<a href="/register" class="hover:text-primary">Kayıt Ol</a>
				<a href="/login" class="hover:text-primary">Giriş Yap</a>
				<a href="/terms" class="hover:text-primary">Kullanım Koşulları</a>
				<a href="/privacy" class="hover:text-primary">Gizlilik Politikası</a>
			</nav>
		</div>
		<p class="mt-6 text-center text-xs text-neutral-400">
			© {new Date().getFullYear()} SadeceFanlar · Sadece 18+ · Monero & Bitcoin
		</p>
	</footer>
</div>
