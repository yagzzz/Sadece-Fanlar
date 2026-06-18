import { c as create_ssr_component, a as subscribe, f as escape, v as validate_component, e as each } from './ssr-DDQ8otPt.js';
import { a as api } from './index2-DIqK_D2c.js';
import { a as authStore } from './auth-C_KGpDdi.js';
import { P as PostCard } from './PostCard-De8q1WfN.js';
import 'clsx';
import { B as Button } from './Button-DeTt_asi.js';
import { S as Spinner } from './Spinner-DOBAUkHr.js';
import { S as Skeleton } from './Skeleton-1_Puv0XT.js';
import 'tailwind-merge';
import './index-BCAmX91C.js';
import './Avatar-a6pAu8NW.js';

const Landing = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  return `<div class="max-w-2xl mx-auto px-4 py-16 sm:py-24"><section class="text-center mb-16"><h1 class="text-3xl sm:text-4xl font-semibold tracking-tight text-neutral-900 dark:text-white mb-4" data-svelte-h="svelte-q2opje">İçerik üreticileri için anonim abonelik platformu</h1> <p class="text-neutral-600 dark:text-neutral-400 text-lg mb-8 max-w-xl mx-auto" data-svelte-h="svelte-177vcds">E-posta veya kimlik gerekmez. Ödemeler yalnızca kripto ile yapılır.</p> <div class="flex flex-col sm:flex-row gap-3 justify-center">${validate_component(Button, "Button").$$render($$result, { href: "/register", size: "lg" }, {}, {
    default: () => {
      return `Hesap oluştur`;
    }
  })} ${validate_component(Button, "Button").$$render(
    $$result,
    {
      href: "/login",
      variant: "outline",
      size: "lg"
    },
    {},
    {
      default: () => {
        return `Giriş yap`;
      }
    }
  )}</div></section> <section class="grid sm:grid-cols-3 gap-6 mb-16 text-sm" data-svelte-h="svelte-sxdt8n"><div class="border border-neutral-200 dark:border-neutral-800 rounded-lg p-5"><p class="font-medium mb-2">Anonim kayıt</p> <p class="text-neutral-500">Kullanıcı adı ve şifre yeterli. E-posta isteğe bağlı.</p></div> <div class="border border-neutral-200 dark:border-neutral-800 rounded-lg p-5"><p class="font-medium mb-2">Kripto ödeme</p> <p class="text-neutral-500">Monero ve Bitcoin. Kart veya banka bilgisi yok.</p></div> <div class="border border-neutral-200 dark:border-neutral-800 rounded-lg p-5"><p class="font-medium mb-2">Üretici odaklı</p> <p class="text-neutral-500">Abonelik, bahşiş ve kilitli içerik ile kazan.</p></div></section> <section class="border-t border-neutral-200 dark:border-neutral-800 pt-10 text-center text-sm text-neutral-500" data-svelte-h="svelte-bh2urt"><p class="mb-3">18 yaş ve üzeri içindir. Yasadışı içerik yasaktır.</p> <div class="flex justify-center gap-4"><a href="/terms" class="hover:text-neutral-800 dark:hover:text-neutral-300">Kullanım Şartları</a> <a href="/privacy" class="hover:text-neutral-800 dark:hover:text-neutral-300">Gizlilik</a></div></section></div>`;
});
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let isReady;
  let isLoggedIn;
  let $authStore, $$unsubscribe_authStore;
  $$unsubscribe_authStore = subscribe(authStore, (value) => $authStore = value);
  let posts = [];
  let loading = true;
  let loadingMore = false;
  let hasMore = true;
  let page = 1;
  async function loadPosts() {
    try {
      const response = await api.posts.getFeed(page, 20);
      posts = [...posts, ...response.items];
      hasMore = response.items.length === 20;
    } catch (err) {
      console.error("Failed to load posts:", err);
    } finally {
      loading = false;
      loadingMore = false;
    }
  }
  let started = false;
  isReady = $authStore.initialized;
  isLoggedIn = !!$authStore.user;
  {
    if (isReady) {
      if (isLoggedIn && !started) {
        started = true;
        loadPosts();
      } else if (!isLoggedIn) {
        loading = false;
      }
    }
  }
  $$unsubscribe_authStore();
  return `${$$result.head += `<!-- HEAD_svelte-1o3phmz_START -->${$$result.title = `<title>${escape(isLoggedIn ? "Akış" : "SadeceFanlar — Anonim, kripto tabanlı içerik platformu")} | SadeceFanlar</title>`, ""}<!-- HEAD_svelte-1o3phmz_END -->`, ""} ${isReady && !isLoggedIn ? `${validate_component(Landing, "Landing").$$render($$result, {}, {}, {})}` : `<div class="p-4 space-y-4"> ${$authStore.user ? `<div class="bg-white dark:bg-neutral-900 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-800 p-4" data-svelte-h="svelte-se2l4o"><a href="/new-post" class="flex items-center gap-3 text-neutral-400 hover:text-neutral-500 transition-colors"><div class="w-10 h-10 rounded-full bg-neutral-100 dark:bg-neutral-800"></div> <span>Aklınızdan ne geçiyor?</span></a></div>` : ``}  ${loading ? `${each(Array(3), (_) => {
    return `<div class="bg-white dark:bg-neutral-900 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-800 p-4 space-y-4"><div class="flex items-center gap-3">${validate_component(Skeleton, "Skeleton").$$render(
      $$result,
      {
        variant: "circular",
        width: "48px",
        height: "48px"
      },
      {},
      {}
    )} <div class="flex-1">${validate_component(Skeleton, "Skeleton").$$render($$result, { width: "120px" }, {}, {})} ${validate_component(Skeleton, "Skeleton").$$render($$result, { width: "80px", class: "mt-1" }, {}, {})} </div></div> ${validate_component(Skeleton, "Skeleton").$$render($$result, { lines: 2 }, {}, {})} ${validate_component(Skeleton, "Skeleton").$$render($$result, { variant: "rectangular", height: "300px" }, {}, {})} </div>`;
  })}` : `${posts.length === 0 ? `<div class="text-center py-12"><p class="text-4xl mb-4" data-svelte-h="svelte-fwdii7">📭</p> <h2 class="text-xl font-semibold text-neutral-900 dark:text-white mb-2" data-svelte-h="svelte-14easun">Akışınız boş</h2> <p class="text-neutral-500 mb-4" data-svelte-h="svelte-1izderj">İçerik üreticilerine abone olarak gönderilerini burada görün.</p> ${validate_component(Button, "Button").$$render($$result, { href: "/explore" }, {}, {
    default: () => {
      return `İçerik Üreticilerini Keşfet`;
    }
  })}</div>` : `${each(posts, (post) => {
    return `${validate_component(PostCard, "PostCard").$$render($$result, { post }, {}, {})}`;
  })}  ${hasMore ? `<div class="flex justify-center py-4">${loadingMore ? `${validate_component(Spinner, "Spinner").$$render($$result, {}, {}, {})}` : `${validate_component(Button, "Button").$$render($$result, { variant: "ghost" }, {}, {
    default: () => {
      return `Daha Fazla Yükle`;
    }
  })}`}</div>` : ``}`}`}</div>`}`;
});

export { Page as default };
//# sourceMappingURL=_page.svelte-UDYvNzXW.js.map
