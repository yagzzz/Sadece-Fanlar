import { c as create_ssr_component, a as subscribe, e as each, f as escape, d as add_attribute, v as validate_component } from './ssr-DDQ8otPt.js';
import { p as page } from './stores-vS07tqvC.js';
import { a as authStore } from './auth-C_KGpDdi.js';
import { w as writable } from './index-BCAmX91C.js';
import { B as Button } from './Button-DeTt_asi.js';
import { c as cn } from './index2-DIqK_D2c.js';
import { A as Avatar } from './Avatar-a6pAu8NW.js';
import { i as isAdmin } from './auth2-Ezum3S4H.js';
import './ssr2-CJcMdXvQ.js';
import './state.svelte-DYGtfCg5.js';
import 'clsx';
import 'tailwind-merge';

function createTheme() {
  const initial = "dark";
  const { subscribe: subscribe2, set } = writable(initial);
  function apply(value) {
    set(value);
  }
  return {
    subscribe: subscribe2,
    set: apply,
    toggle: () => {
      return;
    }
  };
}
const theme = createTheme();
const Layout = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let user;
  let currentPath;
  let isLanding;
  let $page, $$unsubscribe_page;
  let $authStore, $$unsubscribe_authStore;
  let $theme, $$unsubscribe_theme;
  $$unsubscribe_page = subscribe(page, (value) => $page = value);
  $$unsubscribe_authStore = subscribe(authStore, (value) => $authStore = value);
  $$unsubscribe_theme = subscribe(theme, (value) => $theme = value);
  const navItems = [
    { href: "/", label: "Ana Sayfa" },
    { href: "/explore", label: "Keşfet" },
    {
      href: "/messages",
      label: "Mesajlar",
      auth: true
    },
    {
      href: "/notifications",
      label: "Bildirimler",
      auth: true
    },
    {
      href: "/wallet",
      label: "Cüzdan",
      auth: true
    }
  ];
  function navClass(href) {
    const active = href === "/" ? currentPath === "/" : currentPath.startsWith(href);
    return cn("block px-3 py-2 text-sm rounded-md transition-colors", active ? "bg-neutral-100 dark:bg-neutral-800 text-neutral-900 dark:text-white font-medium" : "text-neutral-600 dark:text-neutral-400 hover:bg-neutral-50 dark:hover:bg-neutral-800/60");
  }
  user = $authStore.user;
  currentPath = $page.url.pathname;
  isLanding = currentPath === "/" && !user;
  $$unsubscribe_page();
  $$unsubscribe_authStore();
  $$unsubscribe_theme();
  return `<div class="min-h-screen bg-white dark:bg-neutral-950 text-neutral-900 dark:text-neutral-100"><aside class="hidden lg:fixed lg:inset-y-0 lg:left-0 lg:flex lg:w-56 lg:flex-col border-r border-neutral-200 dark:border-neutral-800"><div class="flex flex-col h-full px-4 py-5"><a href="/" class="px-3 mb-8 text-lg font-semibold tracking-tight" data-svelte-h="svelte-1sa8eyv">SadeceFanlar</a> <nav class="flex-1 space-y-1">${each(navItems, (item) => {
    return `${!item.auth || user ? `<a${add_attribute("href", item.href, 0)}${add_attribute("class", navClass(item.href), 0)}>${escape(item.label)}</a>` : ``}`;
  })} ${user ? `<a href="${"/" + escape(user.username, true)}"${add_attribute("class", navClass(`/${user.username}`), 0)}>Profilim</a> <a href="/settings"${add_attribute("class", navClass("/settings"), 0)}>Ayarlar</a> ${isAdmin(user) ? `<a href="/settings?tab=site"${add_attribute("class", navClass("/settings?tab=site"), 0)}>Site Ayarları</a>` : ``}` : ``}</nav> <button type="button" class="flex items-center gap-2 w-full px-3 py-2 mb-2 text-sm text-neutral-600 dark:text-neutral-400 hover:bg-neutral-50 dark:hover:bg-neutral-800/60 rounded-md transition-colors">${$theme === "dark" ? `☀️ Aydınlık tema` : `🌙 Karanlık tema`}</button> <div class="pt-4 border-t border-neutral-200 dark:border-neutral-800">${user ? `<div class="flex items-center gap-3 px-3 py-2 mb-3">${validate_component(Avatar, "Avatar").$$render(
    $$result,
    {
      src: user.avatar_url,
      alt: user.display_name,
      size: "sm"
    },
    {},
    {}
  )} <div class="min-w-0"><p class="text-sm font-medium truncate">${escape(user.display_name || user.username)}</p> <p class="text-xs text-neutral-500 truncate">@${escape(user.username)}</p></div></div> ${user.is_creator ? `${validate_component(Button, "Button").$$render(
    $$result,
    {
      href: "/new-post",
      class: "w-full mb-2",
      size: "sm"
    },
    {},
    {
      default: () => {
        return `Yeni gönderi`;
      }
    }
  )}` : ``} <button type="button" class="w-full text-left px-3 py-2 text-sm text-neutral-500 hover:text-neutral-900 dark:hover:text-white" data-svelte-h="svelte-ogabtr">Çıkış yap</button>` : `<div class="space-y-2">${validate_component(Button, "Button").$$render(
    $$result,
    {
      href: "/login",
      class: "w-full",
      size: "sm"
    },
    {},
    {
      default: () => {
        return `Giriş yap`;
      }
    }
  )} ${validate_component(Button, "Button").$$render(
    $$result,
    {
      href: "/register",
      variant: "outline",
      class: "w-full",
      size: "sm"
    },
    {},
    {
      default: () => {
        return `Kayıt ol`;
      }
    }
  )}</div>`}</div></div></aside> <header class="lg:hidden sticky top-0 z-40 border-b border-neutral-200 dark:border-neutral-800 bg-white/95 dark:bg-neutral-950/95 backdrop-blur"><div class="flex items-center justify-between h-14 px-4"><a href="/" class="font-semibold" data-svelte-h="svelte-uksp06">SadeceFanlar</a> ${user ? `<div class="flex items-center gap-3 text-sm" data-svelte-h="svelte-44cmq"><a href="/wallet" class="text-neutral-600 dark:text-neutral-300">Cüzdan</a> <a href="/settings" class="text-neutral-600 dark:text-neutral-300">Ayarlar</a></div>` : `${validate_component(Button, "Button").$$render($$result, { href: "/login", size: "sm" }, {}, {
    default: () => {
      return `Giriş`;
    }
  })}`}</div></header> <nav class="lg:hidden fixed bottom-0 inset-x-0 z-40 border-t border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-950"><div class="grid grid-cols-5 h-14 text-xs">${each(navItems.slice(0, 4), (item) => {
    return `${!item.auth || user ? `<a${add_attribute("href", item.href, 0)} class="flex flex-col items-center justify-center gap-0.5 text-neutral-500"><span${add_attribute(
      "class",
      currentPath === item.href || item.href !== "/" && currentPath.startsWith(item.href) ? "text-neutral-900 dark:text-white font-medium" : "",
      0
    )}>${escape(item.label)}</span> </a>` : ``}`;
  })} ${user ? `<a href="/wallet" class="flex flex-col items-center justify-center text-neutral-500"><span${add_attribute(
    "class",
    currentPath.startsWith("/wallet") ? "text-neutral-900 dark:text-white font-medium" : "",
    0
  )}>Cüzdan</span></a>` : `<a href="/login" class="flex flex-col items-center justify-center text-neutral-500" data-svelte-h="svelte-1i5x14p">Giriş</a>`}</div></nav> <main class="lg:pl-56 pt-0 pb-16 lg:pb-0"><div${add_attribute("class", isLanding ? "w-full" : "max-w-3xl mx-auto px-4 py-6", 0)}>${slots.default ? slots.default({}) : ``}</div></main></div>`;
});

export { Layout as default };
//# sourceMappingURL=_layout.svelte-CfWDXH4S.js.map
