import { c as create_ssr_component, a as subscribe } from './ssr-CxJiF8w8.js';
import { a as authStore } from './auth-1cButIF9.js';
import './index-YI0dIwkT.js';
import './client-DAdgJWpw.js';

const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let $authStore, $$unsubscribe_authStore;
  $$unsubscribe_authStore = subscribe(authStore, (value) => $authStore = value);
  $authStore.user;
  $$unsubscribe_authStore();
  return `${$$result.head += `<!-- HEAD_svelte-11m878f_START -->${$$result.title = `<title>Hesap Askıya Alındı</title>`, ""}<meta name="robots" content="noindex, nofollow"><!-- HEAD_svelte-11m878f_END -->`, ""} <div class="min-h-screen flex items-center justify-center bg-gradient-to-b from-red-950 via-neutral-950 to-black px-6 text-center"><div class="max-w-lg"><div class="text-7xl mb-6" data-svelte-h="svelte-yvn1ym">🚫</div> <h1 class="text-3xl sm:text-4xl font-extrabold text-red-500 mb-4" data-svelte-h="svelte-ehudyf">Hesabınız Askıya Alındı</h1> <p class="text-neutral-300 text-lg mb-6 leading-relaxed" data-svelte-h="svelte-575ua7">Sistemimiz hesabınızda <strong class="text-red-400">izinsiz ekran görüntüsü / kayıt girişimi</strong>
			tespit etti. İçerik üreticilerinin emeğini çalmaya çalışmak bu platformda
			<strong class="text-white">en ağır ihlaldir.</strong></p> <div class="bg-black/40 border border-red-900 rounded-xl p-5 mb-6 text-left" data-svelte-h="svelte-g2rw70"><p class="text-neutral-400 text-sm mb-2">⚠️ Bilmeniz gerekenler:</p> <ul class="text-neutral-300 text-sm space-y-1 list-disc list-inside"><li>Tüm içeriklerde kimliğinize özel görünmez filigran bulunur.</li> <li>Sızdırılan her görüntü doğrudan sizinle ilişkilendirilebilir.</li> <li>Bakiyeniz ve erişiminiz donduruldu.</li></ul></div> <p class="text-neutral-500 text-sm mb-8" data-svelte-h="svelte-1mzjdwc">Bunun bir hata olduğunu düşünüyorsanız destek ekibine yazın. O zamana kadar
			bu sayfa dışındaki hiçbir alana erişemezsiniz.</p> <button class="px-6 py-3 rounded-lg bg-neutral-800 text-neutral-200 hover:bg-neutral-700 transition-colors" data-svelte-h="svelte-1fc9mfi">Çıkış yap</button></div></div>`;
});

export { Page as default };
//# sourceMappingURL=_page.svelte-6pnHRXGK.js.map
