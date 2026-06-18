import { c as create_ssr_component, a as subscribe, f as escape, v as validate_component, d as add_attribute, e as each, b as createEventDispatcher } from './ssr-DDQ8otPt.js';
import { p as page } from './stores-vS07tqvC.js';
import { a as api, f as formatCurrency, c as cn } from './index2-BnafdvHM.js';
import { a as authStore } from './auth-D1fv4cSm.js';
import { B as Badge, P as PostCard } from './PostCard-pS-uXsMm.js';
import { B as Button } from './Button-0QyeOH-3.js';
import { A as Avatar } from './Avatar-CJBrCmrS.js';
import { S as Skeleton } from './Skeleton-CbUQ4TvO.js';
import { T as Tabs } from './Tabs-CukORenJ.js';
import 'clsx';
import { S as Spinner } from './Spinner-D9HjBBlQ.js';
import './ssr2-CJcMdXvQ.js';
import './state.svelte-DYGtfCg5.js';
import 'tailwind-merge';
import './index-BCAmX91C.js';

const Modal = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { open = false } = $$props;
  let { title = "" } = $$props;
  let { description = "" } = $$props;
  let { class: className = "" } = $$props;
  if ($$props.open === void 0 && $$bindings.open && open !== void 0) $$bindings.open(open);
  if ($$props.title === void 0 && $$bindings.title && title !== void 0) $$bindings.title(title);
  if ($$props.description === void 0 && $$bindings.description && description !== void 0) $$bindings.description(description);
  if ($$props.class === void 0 && $$bindings.class && className !== void 0) $$bindings.class(className);
  return ` ${open ? ` <div class="fixed inset-0 z-50 flex items-center justify-center" role="dialog" aria-modal="true"> <div class="fixed inset-0 bg-black/50 backdrop-blur-sm" role="button" aria-label="Close modal" tabindex="0"></div>  <div${add_attribute("class", cn("relative z-50 mx-4 w-full max-w-lg rounded-xl bg-card p-6 shadow-lg", className), 0)}> <button class="absolute right-4 top-4 rounded-lg p-1 text-muted-foreground hover:bg-muted hover:text-foreground" data-svelte-h="svelte-1deqviz"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"></path><path d="m6 6 12 12"></path></svg></button>  ${title || description ? `<div class="mb-4">${title ? `<h2 class="text-lg font-semibold">${escape(title)}</h2>` : ``} ${description ? `<p class="mt-1 text-sm text-muted-foreground">${escape(description)}</p>` : ``}</div>` : ``}  ${slots.default ? slots.default({}) : ``}</div></div>` : ``}`;
});
const SubscribeModal = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { open = false } = $$props;
  let { user } = $$props;
  let { class: className = "" } = $$props;
  createEventDispatcher();
  if ($$props.open === void 0 && $$bindings.open && open !== void 0) $$bindings.open(open);
  if ($$props.user === void 0 && $$bindings.user && user !== void 0) $$bindings.user(user);
  if ($$props.class === void 0 && $$bindings.class && className !== void 0) $$bindings.class(className);
  return `${validate_component(Modal, "Modal").$$render(
    $$result,
    {
      open,
      title: user.display_name + " Aboneliği",
      class: className
    },
    {},
    {
      default: () => {
        return `${`<div class="flex items-center justify-center py-12">${validate_component(Spinner, "Spinner").$$render($$result, { size: "lg" }, {}, {})}</div>`}`;
      }
    }
  )}`;
});
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let username;
  let isOwnProfile;
  let $authStore, $$unsubscribe_authStore;
  let $page, $$unsubscribe_page;
  $$unsubscribe_authStore = subscribe(authStore, (value) => $authStore = value);
  $$unsubscribe_page = subscribe(page, (value) => $page = value);
  let user = null;
  let posts = [];
  let loading = true;
  let loadingPosts = true;
  let activeTab = "posts";
  let showSubscribeModal = false;
  const tabs = [
    {
      id: "posts",
      label: "📝 Gönderiler"
    },
    { id: "media", label: "📷 Medya" },
    { id: "locked", label: "🔒 Kilitli" }
  ];
  async function loadUser() {
    loading = true;
    try {
      user = await api.users.getByUsername(username);
    } catch (err) {
      console.error("Failed to load user:", err);
    } finally {
      loading = false;
    }
  }
  async function loadPosts() {
    if (!user) return;
    loadingPosts = true;
    try {
      const response = await api.posts.getByUser(user.username, {
        filter: activeTab === "media" ? "media" : activeTab === "locked" ? "locked" : void 0
      });
      posts = response.items;
    } catch (err) {
      console.error("Failed to load posts:", err);
    } finally {
      loadingPosts = false;
    }
  }
  let $$settled;
  let $$rendered;
  let previous_head = $$result.head;
  do {
    $$settled = true;
    $$result.head = previous_head;
    username = $page.params.username;
    isOwnProfile = $authStore.user?.username === username;
    {
      if (user) loadPosts();
    }
    {
      if (username) loadUser();
    }
    $$rendered = `${$$result.head += `<!-- HEAD_svelte-18b6yzr_START -->${$$result.title = `<title>${escape(user?.display_name || username)} | SadeceFanlar</title>`, ""}<meta name="robots" content="noindex, nofollow"><!-- HEAD_svelte-18b6yzr_END -->`, ""} ${loading ? `<div class="animate-pulse">${validate_component(Skeleton, "Skeleton").$$render($$result, { variant: "rectangular", height: "200px" }, {}, {})} <div class="p-4 -mt-16">${validate_component(Skeleton, "Skeleton").$$render(
      $$result,
      {
        variant: "circular",
        width: "100px",
        height: "100px"
      },
      {},
      {}
    )} ${validate_component(Skeleton, "Skeleton").$$render($$result, { width: "40%", class: "mt-4" }, {}, {})} ${validate_component(Skeleton, "Skeleton").$$render($$result, { width: "30%", class: "mt-2" }, {}, {})} ${validate_component(Skeleton, "Skeleton").$$render($$result, { lines: 2, class: "mt-4" }, {}, {})}</div></div>` : `${!user ? `<div class="text-center py-20"><p class="text-4xl mb-4" data-svelte-h="svelte-11dflqo">🤷</p> <h2 class="text-xl font-semibold text-neutral-900 dark:text-white mb-2" data-svelte-h="svelte-1j1y39r">Kullanıcı bulunamadı</h2> <p class="text-neutral-500 mb-4" data-svelte-h="svelte-17ljros">Aradığınız profil mevcut değil.</p> ${validate_component(Button, "Button").$$render($$result, { href: "/explore" }, {}, {
      default: () => {
        return `İçerik Üreticilerini Keşfet`;
      }
    })}</div>` : ` <div class="relative h-48 bg-gradient-to-r from-primary/50 to-primary">${user.cover_url ? `<img${add_attribute("src", user.cover_url, 0)} alt="Cover" class="w-full h-full object-cover">` : ``}</div>  <div class="px-4 pb-4 -mt-16 relative"><div class="flex items-end gap-4 mb-4">${validate_component(Avatar, "Avatar").$$render(
      $$result,
      {
        src: user.avatar_url,
        alt: user.display_name,
        size: "lg",
        class: "w-24 h-24 border-4 border-white dark:border-neutral-900"
      },
      {},
      {}
    )} <div class="flex-1 flex items-center gap-2 pb-2">${isOwnProfile ? `${validate_component(Button, "Button").$$render(
      $$result,
      {
        href: "/settings",
        variant: "outline",
        size: "sm"
      },
      {},
      {
        default: () => {
          return `Profili Düzenle`;
        }
      }
    )}` : `${user.is_subscribed ? `${validate_component(Button, "Button").$$render($$result, { variant: "secondary", size: "sm" }, {}, {
      default: () => {
        return `💬 Mesaj`;
      }
    })}` : `${validate_component(Button, "Button").$$render($$result, { size: "sm" }, {}, {
      default: () => {
        return `Abone Ol`;
      }
    })}`} ${validate_component(Button, "Button").$$render(
      $$result,
      {
        variant: user.is_following ? "outline" : "secondary",
        size: "sm"
      },
      {},
      {
        default: () => {
          return `${escape(user.is_following ? "Takip Ediliyor" : "Takip Et")}`;
        }
      }
    )}`}</div></div> <div class="mb-4"><div class="flex items-center gap-2"><h1 class="text-2xl font-bold text-neutral-900 dark:text-white">${escape(user.display_name)}</h1> ${user.is_verified ? `${validate_component(Badge, "Badge").$$render($$result, { variant: "primary" }, {}, {
      default: () => {
        return `✓ Doğrulanmış`;
      }
    })}` : ``}</div> <p class="text-neutral-500">@${escape(user.username)}</p></div> ${user.bio ? `<p class="text-neutral-700 dark:text-neutral-300 mb-4 whitespace-pre-wrap">${escape(user.bio)}</p>` : ``}  <div class="flex items-center gap-6 text-sm mb-4"><div><span class="font-bold text-neutral-900 dark:text-white">${escape(user.posts_count || 0)}</span> <span class="text-neutral-500" data-svelte-h="svelte-1hq7mp3">gönderi</span></div> <div><span class="font-bold text-neutral-900 dark:text-white">${escape(user.subscribers_count || 0)}</span> <span class="text-neutral-500" data-svelte-h="svelte-19h65ql">abone</span></div> <div><span class="font-bold text-neutral-900 dark:text-white">${escape(user.media_count || 0)}</span> <span class="text-neutral-500" data-svelte-h="svelte-lswbxk">medya</span></div></div>  ${!isOwnProfile && !user.is_subscribed ? `<div class="bg-primary/5 border border-primary/20 rounded-xl p-4 mb-4"><div class="flex items-center justify-between"><div><p class="font-medium text-neutral-900 dark:text-white" data-svelte-h="svelte-al6hu0">Tam erişim için abone olun</p> <p class="text-sm text-neutral-500">${escape(user.subscription_price ? `${formatCurrency(user.subscription_price)}/ay` : "Ücretsiz")}</p></div> ${validate_component(Button, "Button").$$render($$result, {}, {}, {
      default: () => {
        return `Şimdi Abone Ol`;
      }
    })}</div></div>` : ``}</div>  <div class="px-4">${validate_component(Tabs, "Tabs").$$render(
      $$result,
      { tabs, activeTab },
      {
        activeTab: ($$value) => {
          activeTab = $$value;
          $$settled = false;
        }
      },
      {
        default: () => {
          return `${loadingPosts ? `<div class="space-y-4">${each(Array(3), (_) => {
            return `<div class="bg-white dark:bg-neutral-900 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-800 p-4 space-y-4">${validate_component(Skeleton, "Skeleton").$$render($$result, { lines: 2 }, {}, {})} ${validate_component(Skeleton, "Skeleton").$$render($$result, { variant: "rectangular", height: "200px" }, {}, {})} </div>`;
          })}</div>` : `${posts.length === 0 ? `<div class="text-center py-12"><p class="text-4xl mb-4" data-svelte-h="svelte-fwdii7">📭</p> <p class="text-neutral-500">${escape(activeTab === "posts" ? "Henüz gönderi yok." : activeTab === "media" ? "Henüz medya içerikli gönderi yok." : "Kilitli içerik yok.")}</p></div>` : `<div class="space-y-4 pb-8">${each(posts, (post) => {
            return `${validate_component(PostCard, "PostCard").$$render($$result, { post, showCreator: false }, {}, {})}`;
          })}</div>`}`}`;
        }
      }
    )}</div>  ${user ? `${validate_component(SubscribeModal, "SubscribeModal").$$render(
      $$result,
      { user, open: showSubscribeModal },
      {
        open: ($$value) => {
          showSubscribeModal = $$value;
          $$settled = false;
        }
      },
      {}
    )}` : ``}`}`}`;
  } while (!$$settled);
  $$unsubscribe_authStore();
  $$unsubscribe_page();
  return $$rendered;
});

export { Page as default };
//# sourceMappingURL=_page.svelte-CPxH6yWV.js.map
