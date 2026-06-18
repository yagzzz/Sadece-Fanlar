import { c as create_ssr_component, d as add_attribute, a as subscribe, b as createEventDispatcher, f as escape, v as validate_component, e as each } from './ssr-DDQ8otPt.js';
import { c as cn, t as timeAgo, f as formatCurrency } from './index2-BnafdvHM.js';
import { B as Button } from './Button-0QyeOH-3.js';
import { A as Avatar } from './Avatar-CJBrCmrS.js';
import { a as authStore } from './auth-D1fv4cSm.js';

const Badge = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { variant = "default" } = $$props;
  let { class: className = "" } = $$props;
  const variants = {
    default: "bg-secondary text-secondary-foreground",
    primary: "bg-primary/10 text-primary",
    success: "bg-green-500/10 text-green-500",
    warning: "bg-yellow-500/10 text-yellow-500",
    error: "bg-red-500/10 text-red-500",
    outline: "border border-input bg-transparent"
  };
  if ($$props.variant === void 0 && $$bindings.variant && variant !== void 0) $$bindings.variant(variant);
  if ($$props.class === void 0 && $$bindings.class && className !== void 0) $$bindings.class(className);
  return `<span${add_attribute("class", cn("inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors", variants[variant], className), 0)}>${slots.default ? slots.default({}) : ``}</span>`;
});
const Dropdown = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { items } = $$props;
  let { align = "right" } = $$props;
  let { class: className = "" } = $$props;
  createEventDispatcher();
  if ($$props.items === void 0 && $$bindings.items && items !== void 0) $$bindings.items(items);
  if ($$props.align === void 0 && $$bindings.align && align !== void 0) $$bindings.align(align);
  if ($$props.class === void 0 && $$bindings.class && className !== void 0) $$bindings.class(className);
  return ` <div${add_attribute("class", cn("relative inline-block text-left", className), 0)}><div role="button" tabindex="0">${slots.trigger ? slots.trigger({}) : ` <button type="button" class="inline-flex items-center justify-center p-2 rounded-md text-neutral-400 hover:text-neutral-500 hover:bg-neutral-100 dark:hover:bg-neutral-800" data-svelte-h="svelte-1t7t7uc"><svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z"></path></svg></button> `}</div> ${``}</div>`;
});
const PostCard = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let creator;
  let isLocked;
  let isOwner;
  let mediaCount;
  let currentMediaIndex;
  let $authStore, $$unsubscribe_authStore;
  $$unsubscribe_authStore = subscribe(authStore, (value) => $authStore = value);
  let { post } = $$props;
  let { showCreator = true } = $$props;
  let { class: className = "" } = $$props;
  createEventDispatcher();
  const dropdownItems = [
    {
      id: "share",
      label: "Paylaş",
      icon: "📤"
    },
    {
      id: "report",
      label: "Şikayet Et",
      icon: "🚩",
      danger: true
    },
    ...isOwner ? [
      { id: "divider", label: "", divider: true },
      {
        id: "edit",
        label: "Düzenle",
        icon: "✏️"
      },
      {
        id: "delete",
        label: "Sil",
        icon: "🗑️",
        danger: true
      }
    ] : []
  ];
  if ($$props.post === void 0 && $$bindings.post && post !== void 0) $$bindings.post(post);
  if ($$props.showCreator === void 0 && $$bindings.showCreator && showCreator !== void 0) $$bindings.showCreator(showCreator);
  if ($$props.class === void 0 && $$bindings.class && className !== void 0) $$bindings.class(className);
  creator = post.author ?? post.user;
  isLocked = (post.is_ppv || post.is_premium) && !post.is_unlocked;
  isOwner = $authStore.user?.id === (creator?.id ?? post.user_id);
  mediaCount = post.media?.length || 0;
  currentMediaIndex = 0;
  $$unsubscribe_authStore();
  return `<article${add_attribute("class", cn("bg-white dark:bg-neutral-900 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-800 overflow-hidden", className), 0)}> ${showCreator ? `<div class="p-4 flex items-center justify-between"><a href="${"/" + escape(creator?.username, true)}" class="flex items-center gap-3 group">${validate_component(Avatar, "Avatar").$$render(
    $$result,
    {
      src: creator?.avatar_url,
      alt: creator?.display_name,
      size: "md"
    },
    {},
    {}
  )} <div><div class="flex items-center gap-1"><span class="font-semibold text-neutral-900 dark:text-white group-hover:text-primary transition-colors">${escape(creator?.display_name || creator?.username)}</span> ${creator?.is_verified_creator ? `${validate_component(Badge, "Badge").$$render($$result, { variant: "primary", class: "text-xs" }, {}, {
    default: () => {
      return `✓`;
    }
  })}` : ``}</div> <p class="text-sm text-neutral-500">@${escape(creator?.username)} · ${escape(timeAgo(post.created_at))}</p></div></a> ${validate_component(Dropdown, "Dropdown").$$render($$result, { items: dropdownItems }, {}, {})}</div>` : ``}  ${post.text ?? post.content ? `<div class="px-4 pb-3"><p class="text-neutral-800 dark:text-neutral-200 whitespace-pre-wrap">${escape(post.text ?? post.content)}</p></div>` : ``}  ${post.media && post.media.length > 0 ? `<div class="relative aspect-square bg-neutral-100 dark:bg-neutral-800">${isLocked ? ` <div class="absolute inset-0 flex flex-col items-center justify-center bg-neutral-900/80 backdrop-blur-xl"><div class="text-4xl mb-4" data-svelte-h="svelte-lmppts">🔒</div> <p class="text-white text-lg font-medium mb-2" data-svelte-h="svelte-yuvg0d">Premium İçerik</p> <p class="text-neutral-400 mb-4">${escape(formatCurrency(post.ppv_price ?? post.price ?? 0))} ile kilidi aç</p> ${validate_component(Button, "Button").$$render($$result, {}, {}, {
    default: () => {
      return `Kilidi Aç`;
    }
  })}</div>  ${post.media[0].blur_url ? `<img${add_attribute("src", post.media[0].blur_url, 0)} alt="Locked content" class="w-full h-full object-cover filter blur-xl">` : ``}` : ` ${post.media[currentMediaIndex].type === "video" ? `<video${add_attribute("src", post.media[currentMediaIndex].url, 0)} controls class="w-full h-full object-contain bg-black"${add_attribute("poster", post.media[currentMediaIndex].thumbnail_url, 0)}><track kind="captions"></video>` : `<img${add_attribute("src", post.media[currentMediaIndex].url, 0)} alt="Post media" class="w-full h-full object-cover">`}  ${mediaCount > 1 ? `<div class="absolute inset-x-0 top-1/2 -translate-y-1/2 flex justify-between px-2"><button type="button"${add_attribute("class", cn("p-2 rounded-full bg-black/50 text-white hover:bg-black/70 transition-colors", currentMediaIndex === 0 && "opacity-0 pointer-events-none"), 0)}>←</button> <button type="button"${add_attribute("class", cn("p-2 rounded-full bg-black/50 text-white hover:bg-black/70 transition-colors", currentMediaIndex === mediaCount - 1 && "opacity-0 pointer-events-none"), 0)}>→</button></div>  <div class="absolute bottom-4 inset-x-0 flex justify-center gap-1">${each(post.media, (_, i) => {
    return `<button type="button"${add_attribute("class", cn("w-2 h-2 rounded-full transition-colors", i === currentMediaIndex ? "bg-white" : "bg-white/50"), 0)}></button>`;
  })}</div>` : ``}`}</div>` : ``}  <div class="p-4 flex items-center justify-between border-t border-neutral-100 dark:border-neutral-800"><div class="flex items-center gap-4"><button type="button"${add_attribute(
    "class",
    cn("flex items-center gap-1 text-sm transition-colors", post.is_liked ? "text-red-500" : "text-neutral-500 hover:text-red-500"),
    0
  )}><span class="text-xl">${escape(post.is_liked ? "❤️" : "🤍")}</span> <span>${escape(post.likes_count || 0)}</span></button> <button type="button" class="flex items-center gap-1 text-sm text-neutral-500 hover:text-primary transition-colors"><span class="text-xl" data-svelte-h="svelte-rikxs6">💬</span> <span>${escape(post.comments_count || 0)}</span></button> <button type="button" class="flex items-center gap-1 text-sm text-neutral-500 hover:text-green-500 transition-colors" data-svelte-h="svelte-uo7hci"><span class="text-xl">💰</span> <span>Bahşiş</span></button></div> <button type="button"${add_attribute(
    "class",
    cn("text-xl transition-colors", post.is_bookmarked ? "text-yellow-500" : "text-neutral-400 hover:text-yellow-500"),
    0
  )}>${escape(post.is_bookmarked ? "⭐" : "☆")}</button></div></article>`;
});

export { Badge as B, PostCard as P };
//# sourceMappingURL=PostCard-pS-uXsMm.js.map
