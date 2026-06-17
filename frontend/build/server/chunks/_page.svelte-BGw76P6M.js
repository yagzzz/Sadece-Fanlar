import { c as create_ssr_component, o as onDestroy, v as validate_component, e as each, d as add_attribute, f as escape } from './ssr-CAqK4lyn.js';
import { a as api, c as cn, t as timeAgo } from './index2-O1tI1Vis.js';
import { B as Button } from './Button-DYjEXmaK.js';
import { A as Avatar } from './Avatar-Cfr0OREM.js';
import { S as Spinner } from './Spinner-BW-cLHP2.js';
import { T as Tabs } from './Tabs-BRoncGjm.js';
import 'clsx';
import 'tailwind-merge';

function getNotificationIcon(type) {
  switch (type) {
    case "like":
      return "❤️";
    case "comment":
      return "💬";
    case "subscription":
      return "⭐";
    case "tip":
      return "💰";
    case "follow":
      return "👤";
    case "mention":
      return "@";
    default:
      return "🔔";
  }
}
function getNotificationLink(notification) {
  switch (notification.type) {
    case "like":
    case "comment":
      return `/post/${notification.data?.post_id}`;
    case "subscription":
    case "follow":
      return `/${notification.actor?.username}`;
    case "tip":
      return "/wallet";
    default:
      return "#";
  }
}
const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let notifications = [];
  let loading = true;
  let activeTab = "all";
  const tabs = [
    { id: "all", label: "Tümü" },
    {
      id: "likes",
      label: "❤️ Beğeniler"
    },
    {
      id: "comments",
      label: "💬 Yorumlar"
    },
    {
      id: "subscriptions",
      label: "⭐ Abonelikler"
    },
    {
      id: "tips",
      label: "💰 Bahşişler"
    }
  ];
  async function loadNotifications() {
    loading = true;
    try {
      const response = await api.notifications.list({
        type: activeTab !== "all" ? activeTab : void 0
      });
      notifications = response.items;
    } catch (err) {
      console.error("Failed to load notifications:", err);
    } finally {
      loading = false;
    }
  }
  onDestroy(() => {
  });
  let $$settled;
  let $$rendered;
  let previous_head = $$result.head;
  do {
    $$settled = true;
    $$result.head = previous_head;
    {
      if (activeTab) loadNotifications();
    }
    $$rendered = `${$$result.head += `<!-- HEAD_svelte-1wera1y_START -->${$$result.title = `<title>Bildirimler | SadeceFanlar</title>`, ""}<!-- HEAD_svelte-1wera1y_END -->`, ""} <div class="p-4"><div class="flex items-center justify-between mb-6"><h1 class="text-2xl font-bold text-neutral-900 dark:text-white" data-svelte-h="svelte-1dwu50r">Bildirimler</h1> ${notifications.some((n) => !n.is_read) ? `${validate_component(Button, "Button").$$render($$result, { variant: "ghost", size: "sm" }, {}, {
      default: () => {
        return `Tümünü okundu işaretle`;
      }
    })}` : ``}</div> ${validate_component(Tabs, "Tabs").$$render(
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
          return `${loading ? `<div class="flex items-center justify-center py-12">${validate_component(Spinner, "Spinner").$$render($$result, {}, {}, {})}</div>` : `${notifications.length === 0 ? `<div class="text-center py-12" data-svelte-h="svelte-jorxcy"><p class="text-4xl mb-4">🔔</p> <p class="text-neutral-500">Henüz bildirim yok</p></div>` : `<div class="space-y-1">${each(notifications, (notification) => {
            return `<a${add_attribute("href", getNotificationLink(notification), 0)}${add_attribute(
              "class",
              cn("flex items-start gap-3 p-4 rounded-xl transition-colors", notification.is_read ? "bg-transparent hover:bg-neutral-100 dark:hover:bg-neutral-800" : "bg-primary/5 hover:bg-primary/10"),
              0
            )}><div class="relative">${validate_component(Avatar, "Avatar").$$render(
              $$result,
              {
                src: notification.actor?.avatar_url,
                alt: notification.actor?.display_name,
                size: "md"
              },
              {},
              {}
            )} <span class="absolute -bottom-1 -right-1 text-sm">${escape(getNotificationIcon(notification.type))} </span></div> <div class="flex-1 min-w-0"><p class="text-sm text-neutral-900 dark:text-white"><span class="font-semibold">${escape(notification.actor?.display_name)}</span> ${escape(" ")} ${escape(notification.message)}</p> <p class="text-xs text-neutral-500 mt-1">${escape(timeAgo(notification.created_at))} </p></div> ${!notification.is_read ? `<div class="w-2 h-2 bg-primary rounded-full mt-2"></div>` : ``} </a>`;
          })}</div>`}`}`;
        }
      }
    )}</div>`;
  } while (!$$settled);
  return $$rendered;
});

export { Page as default };
//# sourceMappingURL=_page.svelte-BGw76P6M.js.map
