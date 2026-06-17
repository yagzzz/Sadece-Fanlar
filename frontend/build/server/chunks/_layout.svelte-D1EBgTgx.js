import { c as create_ssr_component, a as subscribe, e as each, f as escape, n as null_to_empty, v as validate_component, d as add_attribute } from './ssr-CAqK4lyn.js';
import { p as page } from './stores-qOaUuLm-.js';
import { a as authStore } from './auth-DjJDNFfu.js';
import { B as Button } from './Button-DYjEXmaK.js';
import { c as cn } from './index2-O1tI1Vis.js';
import { A as Avatar } from './Avatar-Cfr0OREM.js';
import { D as Dropdown } from './Dropdown-CH_CmGiA.js';
import './ssr2-CJcMdXvQ.js';
import './state.svelte-DYGtfCg5.js';
import './index-BTslQZ0_.js';
import 'clsx';
import 'tailwind-merge';

const css = {
  code: ".safe-area-pb.svelte-1algusa{padding-bottom:env(safe-area-inset-bottom)}",
  map: `{"version":3,"file":"+layout.svelte","sources":["+layout.svelte"],"sourcesContent":["<script lang=\\"ts\\">import { page } from \\"$app/stores\\";\\nimport { authStore, logout } from \\"$lib/stores/auth\\";\\nimport { Avatar, Badge, Button, Dropdown } from \\"$lib/components/ui\\";\\nimport { cn } from \\"$lib/utils\\";\\n$: user = $authStore.user;\\n$: currentPath = $page.url.pathname;\\n$: isLanding = currentPath === \\"/\\" && !user;\\nconst navItems = [\\n  { href: \\"/\\", label: \\"Ana Sayfa\\", icon: \\"\\\\u{1F3E0}\\" },\\n  { href: \\"/explore\\", label: \\"Ke\\\\u015Ffet\\", icon: \\"\\\\u{1F50D}\\" },\\n  { href: \\"/messages\\", label: \\"Mesajlar\\", icon: \\"\\\\u{1F4AC}\\", auth: true },\\n  { href: \\"/notifications\\", label: \\"Bildirimler\\", icon: \\"\\\\u{1F514}\\", auth: true }\\n];\\nconst userMenuItems = [\\n  { id: \\"profile\\", label: \\"Profilim\\", icon: \\"\\\\u{1F464}\\" },\\n  { id: \\"settings\\", label: \\"Ayarlar\\", icon: \\"\\\\u2699\\\\uFE0F\\" },\\n  { id: \\"wallet\\", label: \\"C\\\\xFCzdan\\", icon: \\"\\\\u{1F4B0}\\" },\\n  { id: \\"divider\\", label: \\"\\", divider: true },\\n  { id: \\"logout\\", label: \\"\\\\xC7\\\\u0131k\\\\u0131\\\\u015F Yap\\", icon: \\"\\\\u{1F6AA}\\", danger: true }\\n];\\nfunction handleUserMenuSelect(e) {\\n  switch (e.detail) {\\n    case \\"profile\\":\\n      window.location.href = \`/\${user?.username}\`;\\n      break;\\n    case \\"settings\\":\\n      window.location.href = \\"/settings\\";\\n      break;\\n    case \\"wallet\\":\\n      window.location.href = \\"/wallet\\";\\n      break;\\n    case \\"logout\\":\\n      logout();\\n      window.location.href = \\"/\\";\\n      break;\\n  }\\n}\\n<\/script>\\n\\n<div class=\\"min-h-screen bg-neutral-50 dark:bg-neutral-950\\">\\n\\t<!-- Desktop Sidebar -->\\n\\t<aside class=\\"hidden lg:fixed lg:inset-y-0 lg:left-0 lg:flex lg:w-64 lg:flex-col\\">\\n\\t\\t<div class=\\"flex flex-col flex-grow border-r border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 pt-5 pb-4 overflow-y-auto\\">\\n\\t\\t\\t<!-- Logo -->\\n\\t\\t\\t<div class=\\"flex items-center flex-shrink-0 px-6\\">\\n\\t\\t\\t\\t<a href=\\"/\\" class=\\"text-2xl font-bold text-primary\\">\\n\\t\\t\\t\\t\\tSadeceFanlar\\n\\t\\t\\t\\t</a>\\n\\t\\t\\t</div>\\n\\n\\t\\t\\t<!-- Navigation -->\\n\\t\\t\\t<nav class=\\"mt-8 flex-1 px-4 space-y-1\\">\\n\\t\\t\\t\\t{#each navItems as item}\\n\\t\\t\\t\\t\\t{#if !item.auth || user}\\n\\t\\t\\t\\t\\t\\t<a\\n\\t\\t\\t\\t\\t\\t\\thref={item.href}\\n\\t\\t\\t\\t\\t\\t\\tclass={cn(\\n\\t\\t\\t\\t\\t\\t\\t\\t'flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-colors',\\n\\t\\t\\t\\t\\t\\t\\t\\tcurrentPath === item.href\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t? 'bg-primary/10 text-primary'\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t: 'text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-800'\\n\\t\\t\\t\\t\\t\\t\\t)}\\n\\t\\t\\t\\t\\t\\t>\\n\\t\\t\\t\\t\\t\\t\\t<span class=\\"text-xl\\">{item.icon}</span>\\n\\t\\t\\t\\t\\t\\t\\t<span>{item.label}</span>\\n\\t\\t\\t\\t\\t\\t</a>\\n\\t\\t\\t\\t\\t{/if}\\n\\t\\t\\t\\t{/each}\\n\\n\\t\\t\\t\\t{#if user}\\n\\t\\t\\t\\t\\t<a\\n\\t\\t\\t\\t\\t\\thref=\\"/{user.username}\\"\\n\\t\\t\\t\\t\\t\\tclass={cn(\\n\\t\\t\\t\\t\\t\\t\\t'flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-colors',\\n\\t\\t\\t\\t\\t\\t\\tcurrentPath === \`/\${user.username}\`\\n\\t\\t\\t\\t\\t\\t\\t\\t? 'bg-primary/10 text-primary'\\n\\t\\t\\t\\t\\t\\t\\t\\t: 'text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-800'\\n\\t\\t\\t\\t\\t\\t)}\\n\\t\\t\\t\\t\\t>\\n\\t\\t\\t\\t\\t\\t<span class=\\"text-xl\\">👤</span>\\n\\t\\t\\t\\t\\t\\t<span>Profil</span>\\n\\t\\t\\t\\t\\t</a>\\n\\t\\t\\t\\t{/if}\\n\\t\\t\\t</nav>\\n\\n\\t\\t\\t<!-- User Section -->\\n\\t\\t\\t<div class=\\"px-4 pb-4\\">\\n\\t\\t\\t\\t{#if user}\\n\\t\\t\\t\\t\\t<Button href=\\"/new-post\\" class=\\"w-full mb-4\\">\\n\\t\\t\\t\\t\\t\\t+ Yeni Gönderi\\n\\t\\t\\t\\t\\t</Button>\\n\\t\\t\\t\\t\\t<Dropdown items={userMenuItems} align=\\"left\\" on:select={handleUserMenuSelect}>\\n\\t\\t\\t\\t\\t\\t<button\\n\\t\\t\\t\\t\\t\\t\\tslot=\\"trigger\\"\\n\\t\\t\\t\\t\\t\\t\\ttype=\\"button\\"\\n\\t\\t\\t\\t\\t\\t\\tclass=\\"flex items-center gap-3 w-full p-3 rounded-xl hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors\\"\\n\\t\\t\\t\\t\\t\\t>\\n\\t\\t\\t\\t\\t\\t\\t<Avatar src={user.avatar_url} alt={user.display_name} size=\\"sm\\" />\\n\\t\\t\\t\\t\\t\\t\\t<div class=\\"flex-1 text-left\\">\\n\\t\\t\\t\\t\\t\\t\\t\\t<p class=\\"text-sm font-medium text-neutral-900 dark:text-white truncate\\">\\n\\t\\t\\t\\t\\t\\t\\t\\t\\t{user.display_name}\\n\\t\\t\\t\\t\\t\\t\\t\\t</p>\\n\\t\\t\\t\\t\\t\\t\\t\\t<p class=\\"text-xs text-neutral-500 truncate\\">@{user.username}</p>\\n\\t\\t\\t\\t\\t\\t\\t</div>\\n\\t\\t\\t\\t\\t\\t\\t<span class=\\"text-neutral-400\\">⋮</span>\\n\\t\\t\\t\\t\\t\\t</button>\\n\\t\\t\\t\\t\\t</Dropdown>\\n\\t\\t\\t\\t{:else}\\n\\t\\t\\t\\t\\t<div class=\\"space-y-2\\">\\n\\t\\t\\t\\t\\t\\t<Button href=\\"/login\\" class=\\"w-full\\">Giriş Yap</Button>\\n\\t\\t\\t\\t\\t\\t<Button href=\\"/register\\" variant=\\"outline\\" class=\\"w-full\\">Kayıt Ol</Button>\\n\\t\\t\\t\\t\\t</div>\\n\\t\\t\\t\\t{/if}\\n\\t\\t\\t</div>\\n\\t\\t</div>\\n\\t</aside>\\n\\n\\t<!-- Mobile Header -->\\n\\t<header class=\\"lg:hidden fixed top-0 inset-x-0 z-40 bg-white dark:bg-neutral-900 border-b border-neutral-200 dark:border-neutral-800\\">\\n\\t\\t<div class=\\"flex items-center justify-between h-16 px-4\\">\\n\\t\\t\\t<a href=\\"/\\" class=\\"text-xl font-bold text-primary\\">SF</a>\\n\\t\\t\\t\\n\\t\\t\\t{#if user}\\n\\t\\t\\t\\t<Dropdown items={userMenuItems} on:select={handleUserMenuSelect}>\\n\\t\\t\\t\\t\\t<button slot=\\"trigger\\" type=\\"button\\" class=\\"p-1\\">\\n\\t\\t\\t\\t\\t\\t<Avatar src={user.avatar_url} alt={user.display_name} size=\\"sm\\" />\\n\\t\\t\\t\\t\\t</button>\\n\\t\\t\\t\\t</Dropdown>\\n\\t\\t\\t{:else}\\n\\t\\t\\t\\t<Button href=\\"/login\\" size=\\"sm\\">Giriş Yap</Button>\\n\\t\\t\\t{/if}\\n\\t\\t</div>\\n\\t</header>\\n\\n\\t<!-- Mobile Bottom Navigation -->\\n\\t<nav class=\\"lg:hidden fixed bottom-0 inset-x-0 z-40 bg-white dark:bg-neutral-900 border-t border-neutral-200 dark:border-neutral-800 safe-area-pb\\">\\n\\t\\t<div class=\\"flex items-center justify-around h-16\\">\\n\\t\\t\\t{#each navItems as item}\\n\\t\\t\\t\\t{#if !item.auth || user}\\n\\t\\t\\t\\t\\t<a\\n\\t\\t\\t\\t\\t\\thref={item.href}\\n\\t\\t\\t\\t\\t\\tclass={cn(\\n\\t\\t\\t\\t\\t\\t\\t'flex flex-col items-center gap-1 px-4 py-2 transition-colors',\\n\\t\\t\\t\\t\\t\\t\\tcurrentPath === item.href\\n\\t\\t\\t\\t\\t\\t\\t\\t? 'text-primary'\\n\\t\\t\\t\\t\\t\\t\\t\\t: 'text-neutral-400'\\n\\t\\t\\t\\t\\t\\t)}\\n\\t\\t\\t\\t\\t>\\n\\t\\t\\t\\t\\t\\t<span class=\\"text-xl\\">{item.icon}</span>\\n\\t\\t\\t\\t\\t\\t<span class=\\"text-xs\\">{item.label}</span>\\n\\t\\t\\t\\t\\t</a>\\n\\t\\t\\t\\t{/if}\\n\\t\\t\\t{/each}\\n\\t\\t\\t{#if user}\\n\\t\\t\\t\\t<a\\n\\t\\t\\t\\t\\thref=\\"/new-post\\"\\n\\t\\t\\t\\t\\tclass=\\"flex flex-col items-center gap-1 px-4 py-2 text-primary\\"\\n\\t\\t\\t\\t>\\n\\t\\t\\t\\t\\t<span class=\\"text-xl\\">➕</span>\\n\\t\\t\\t\\t\\t<span class=\\"text-xs\\">Post</span>\\n\\t\\t\\t\\t</a>\\n\\t\\t\\t{/if}\\n\\t\\t</div>\\n\\t</nav>\\n\\n\\t<!-- Main Content -->\\n\\t<main class=\\"lg:pl-64 pt-16 lg:pt-0 pb-20 lg:pb-0\\">\\n\\t\\t<div class={isLanding ? 'w-full' : 'max-w-2xl mx-auto'}>\\n\\t\\t\\t<slot />\\n\\t\\t</div>\\n\\t</main>\\n</div>\\n\\n<style>\\n\\t.safe-area-pb {\\n\\t\\tpadding-bottom: env(safe-area-inset-bottom);\\n\\t}\\n</style>\\n"],"names":[],"mappings":"AA8KC,4BAAc,CACb,cAAc,CAAE,IAAI,sBAAsB,CAC3C"}`
};
const Layout = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let user;
  let currentPath;
  let isLanding;
  let $page, $$unsubscribe_page;
  let $authStore, $$unsubscribe_authStore;
  $$unsubscribe_page = subscribe(page, (value) => $page = value);
  $$unsubscribe_authStore = subscribe(authStore, (value) => $authStore = value);
  const navItems = [
    {
      href: "/",
      label: "Ana Sayfa",
      icon: "🏠"
    },
    {
      href: "/explore",
      label: "Keşfet",
      icon: "🔍"
    },
    {
      href: "/messages",
      label: "Mesajlar",
      icon: "💬",
      auth: true
    },
    {
      href: "/notifications",
      label: "Bildirimler",
      icon: "🔔",
      auth: true
    }
  ];
  const userMenuItems = [
    {
      id: "profile",
      label: "Profilim",
      icon: "👤"
    },
    {
      id: "settings",
      label: "Ayarlar",
      icon: "⚙️"
    },
    {
      id: "wallet",
      label: "Cüzdan",
      icon: "💰"
    },
    { id: "divider", label: "", divider: true },
    {
      id: "logout",
      label: "Çıkış Yap",
      icon: "🚪",
      danger: true
    }
  ];
  $$result.css.add(css);
  user = $authStore.user;
  currentPath = $page.url.pathname;
  isLanding = currentPath === "/" && !user;
  $$unsubscribe_page();
  $$unsubscribe_authStore();
  return `<div class="min-h-screen bg-neutral-50 dark:bg-neutral-950"> <aside class="hidden lg:fixed lg:inset-y-0 lg:left-0 lg:flex lg:w-64 lg:flex-col"><div class="flex flex-col flex-grow border-r border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 pt-5 pb-4 overflow-y-auto"> <div class="flex items-center flex-shrink-0 px-6" data-svelte-h="svelte-1khap4u"><a href="/" class="text-2xl font-bold text-primary">SadeceFanlar</a></div>  <nav class="mt-8 flex-1 px-4 space-y-1">${each(navItems, (item) => {
    return `${!item.auth || user ? `<a${add_attribute("href", item.href, 0)} class="${escape(
      null_to_empty(cn("flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-colors", currentPath === item.href ? "bg-primary/10 text-primary" : "text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-800")),
      true
    ) + " svelte-1algusa"}"><span class="text-xl">${escape(item.icon)}</span> <span>${escape(item.label)}</span> </a>` : ``}`;
  })} ${user ? `<a href="${"/" + escape(user.username, true)}" class="${escape(
    null_to_empty(cn("flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-colors", currentPath === `/${user.username}` ? "bg-primary/10 text-primary" : "text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-800")),
    true
  ) + " svelte-1algusa"}"><span class="text-xl" data-svelte-h="svelte-1stwn2">👤</span> <span data-svelte-h="svelte-w4x3n4">Profil</span></a>` : ``}</nav>  <div class="px-4 pb-4">${user ? `${validate_component(Button, "Button").$$render($$result, { href: "/new-post", class: "w-full mb-4" }, {}, {
    default: () => {
      return `+ Yeni Gönderi`;
    }
  })} ${validate_component(Dropdown, "Dropdown").$$render($$result, { items: userMenuItems, align: "left" }, {}, {
    trigger: () => {
      return `<button slot="trigger" type="button" class="flex items-center gap-3 w-full p-3 rounded-xl hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors">${validate_component(Avatar, "Avatar").$$render(
        $$result,
        {
          src: user.avatar_url,
          alt: user.display_name,
          size: "sm"
        },
        {},
        {}
      )} <div class="flex-1 text-left"><p class="text-sm font-medium text-neutral-900 dark:text-white truncate">${escape(user.display_name)}</p> <p class="text-xs text-neutral-500 truncate">@${escape(user.username)}</p></div> <span class="text-neutral-400" data-svelte-h="svelte-tbmmnj">⋮</span></button>`;
    }
  })}` : `<div class="space-y-2">${validate_component(Button, "Button").$$render($$result, { href: "/login", class: "w-full" }, {}, {
    default: () => {
      return `Giriş Yap`;
    }
  })} ${validate_component(Button, "Button").$$render(
    $$result,
    {
      href: "/register",
      variant: "outline",
      class: "w-full"
    },
    {},
    {
      default: () => {
        return `Kayıt Ol`;
      }
    }
  )}</div>`}</div></div></aside>  <header class="lg:hidden fixed top-0 inset-x-0 z-40 bg-white dark:bg-neutral-900 border-b border-neutral-200 dark:border-neutral-800"><div class="flex items-center justify-between h-16 px-4"><a href="/" class="text-xl font-bold text-primary" data-svelte-h="svelte-1flafw4">SF</a> ${user ? `${validate_component(Dropdown, "Dropdown").$$render($$result, { items: userMenuItems }, {}, {
    trigger: () => {
      return `<button slot="trigger" type="button" class="p-1">${validate_component(Avatar, "Avatar").$$render(
        $$result,
        {
          src: user.avatar_url,
          alt: user.display_name,
          size: "sm"
        },
        {},
        {}
      )}</button>`;
    }
  })}` : `${validate_component(Button, "Button").$$render($$result, { href: "/login", size: "sm" }, {}, {
    default: () => {
      return `Giriş Yap`;
    }
  })}`}</div></header>  <nav class="lg:hidden fixed bottom-0 inset-x-0 z-40 bg-white dark:bg-neutral-900 border-t border-neutral-200 dark:border-neutral-800 safe-area-pb svelte-1algusa"><div class="flex items-center justify-around h-16">${each(navItems, (item) => {
    return `${!item.auth || user ? `<a${add_attribute("href", item.href, 0)} class="${escape(
      null_to_empty(cn("flex flex-col items-center gap-1 px-4 py-2 transition-colors", currentPath === item.href ? "text-primary" : "text-neutral-400")),
      true
    ) + " svelte-1algusa"}"><span class="text-xl">${escape(item.icon)}</span> <span class="text-xs">${escape(item.label)}</span> </a>` : ``}`;
  })} ${user ? `<a href="/new-post" class="flex flex-col items-center gap-1 px-4 py-2 text-primary" data-svelte-h="svelte-asydbp"><span class="text-xl">➕</span> <span class="text-xs">Post</span></a>` : ``}</div></nav>  <main class="lg:pl-64 pt-16 lg:pt-0 pb-20 lg:pb-0"><div${add_attribute("class", isLanding ? "w-full" : "max-w-2xl mx-auto", 0)}>${slots.default ? slots.default({}) : ``}</div></main> </div>`;
});

export { Layout as default };
//# sourceMappingURL=_layout.svelte-D1EBgTgx.js.map
