<script lang="ts">
	import { Button, Icon } from '$lib/components/ui';

	const features = [
		{ icon: 'shield', title: 'Tam anonim', desc: 'Kimlik, telefon veya kart gerekmez. Kullanıcı adı ve şifre yeterli; e-posta isteğe bağlı.' },
		{ icon: 'zap', title: 'Kripto ödeme', desc: 'Monero (XMR) ile gizli ödeme. Bakiyeniz TL olarak görünür, dalgalanmadan etkilenmezsiniz.' },
		{ icon: 'lock', title: 'Güvenli içerik', desc: 'Kilitli gönderiler, filigranlı medya ve ekran görüntüsü caydırma ile içeriğiniz korunur.' },
		{ icon: 'dollar', title: 'Üretici kazancı', desc: 'Abonelik, bahşiş, kilitli içerik ve emanetli özel istekler ile kazanın. Şeffaf komisyon.' }
	];
</script>

<div class="relative overflow-hidden">
	<!-- Arka plan parıltısı -->
	<div class="pointer-events-none absolute inset-0 -z-10">
		<div class="absolute -top-24 left-1/2 -translate-x-1/2 h-72 w-[40rem] rounded-full bg-primary/20 blur-3xl"></div>
	</div>

	<div class="max-w-3xl mx-auto px-4 py-16 sm:py-24">
		<section class="text-center mb-20">
			<span class="inline-flex items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1 text-xs text-muted-foreground mb-6">
				<Icon name="shield" size={14} class="text-primary" /> Anonim · Kriptolu · 18+
			</span>
			<h1 class="text-4xl sm:text-5xl font-bold tracking-tight mb-5">
				İçeriğini <span class="text-gradient">özgürce</span> paylaş, anonim kazan
			</h1>
			<p class="text-muted-foreground text-lg mb-8 max-w-xl mx-auto">
				Bağımsız içerik üreticileri için anonim abonelik platformu. Kimlik istemez, ödemeler yalnızca kripto ile yapılır.
			</p>
			<div class="flex flex-col sm:flex-row gap-3 justify-center">
				<Button href="/register" size="lg">Hemen başla</Button>
				<Button href="/explore" variant="outline" size="lg">Üreticileri keşfet</Button>
			</div>
		</section>

		<section class="grid sm:grid-cols-2 gap-4 mb-20">
			{#each features as f}
				<div class="rounded-2xl border border-border bg-card p-6 transition-colors hover:border-primary/40">
					<div class="grid place-items-center w-11 h-11 rounded-xl bg-primary/10 text-primary mb-4">
						<Icon name={f.icon} size={22} />
					</div>
					<p class="font-semibold mb-1.5">{f.title}</p>
					<p class="text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
				</div>
			{/each}
		</section>

		<section class="rounded-2xl border border-border bg-card p-8 text-center mb-16">
			<h2 class="text-xl font-semibold mb-2">Üretici olarak kazanmaya başla</h2>
			<p class="text-sm text-muted-foreground mb-5 max-w-md mx-auto">Birkaç dakikada hesabını oluştur, içeriğini yükle ve aboneliklerinle gelir elde et.</p>
			<Button href="/register" size="lg">Ücretsiz hesap oluştur</Button>
		</section>

		<section class="border-t border-border pt-8 text-center text-sm text-muted-foreground">
			<p class="mb-3">Bu platform 18 yaş ve üzeri içindir. Yasadışı içerik kesinlikle yasaktır.</p>
			<div class="flex justify-center gap-5">
				<a href="/terms" class="hover:text-foreground transition-colors">Kullanım Şartları</a>
				<a href="/privacy" class="hover:text-foreground transition-colors">Gizlilik</a>
			</div>
		</section>
	</div>
</div>
