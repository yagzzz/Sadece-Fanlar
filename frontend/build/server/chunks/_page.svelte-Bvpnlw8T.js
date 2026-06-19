import { c as create_ssr_component, v as validate_component, e as each } from './ssr-CxJiF8w8.js';
import './client-CybrWH6X.js';
import 'clsx';
import { I as Input } from './Input-BgLM1v2T.js';
import { S as Skeleton } from './Skeleton-Buq9IvNp.js';
import { T as Tabs } from './Tabs-Ceev7G4w.js';
import './auth-BhyVnWr0.js';
import { A as AdSlot } from './AdSlot-D1T3JLvj.js';
import './index2-Dhq654YE.js';
import 'tailwind-merge';
import './index-YI0dIwkT.js';

const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let searchQuery = "";
  let activeTab = "featured";
  const tabs = [
    {
      id: "featured",
      label: "Öne Çıkanlar"
    },
    { id: "new", label: "Yeni" },
    { id: "popular", label: "Popüler" }
  ];
  let $$settled;
  let $$rendered;
  let previous_head = $$result.head;
  do {
    $$settled = true;
    $$result.head = previous_head;
    $$rendered = `${$$result.head += `<!-- HEAD_svelte-1y54knw_START -->${$$result.title = `<title>İçerik Üreticilerini Keşfet | SadeceFanlar</title>`, ""}<!-- HEAD_svelte-1y54knw_END -->`, ""}  <div class="hidden 2xl:block fixed left-4 top-24 w-40 z-30">${validate_component(AdSlot, "AdSlot").$$render($$result, { position: "explore_left", vertical: true }, {}, {})}</div> <div class="hidden 2xl:block fixed right-4 top-24 w-40 z-30">${validate_component(AdSlot, "AdSlot").$$render(
      $$result,
      {
        position: "explore_right",
        vertical: true
      },
      {},
      {}
    )}</div> <div class="space-y-5"><h1 class="text-xl font-semibold text-neutral-900 dark:text-white" data-svelte-h="svelte-trvm5o">Keşfet</h1> ${validate_component(AdSlot, "AdSlot").$$render($$result, { position: "explore" }, {}, {})}  ${validate_component(Input, "Input").$$render(
      $$result,
      {
        type: "search",
        placeholder: "İçerik üreticisi ara...",
        value: searchQuery
      },
      {
        value: ($$value) => {
          searchQuery = $$value;
          $$settled = false;
        }
      },
      {}
    )}  ${validate_component(Tabs, "Tabs").$$render(
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
          return `${`<div class="grid grid-cols-1 md:grid-cols-2 gap-4">${each(Array(6), (_) => {
            return `<div class="bg-white dark:bg-neutral-900 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-800 overflow-hidden">${validate_component(Skeleton, "Skeleton").$$render($$result, { variant: "rectangular", height: "96px" }, {}, {})} <div class="p-4 pt-12">${validate_component(Skeleton, "Skeleton").$$render($$result, { width: "60%" }, {}, {})} ${validate_component(Skeleton, "Skeleton").$$render($$result, { width: "40%", class: "mt-2" }, {}, {})} ${validate_component(Skeleton, "Skeleton").$$render($$result, { lines: 2, class: "mt-4" }, {}, {})}</div> </div>`;
          })}</div>`}`;
        }
      }
    )}</div>`;
  } while (!$$settled);
  return $$rendered;
});

export { Page as default };
//# sourceMappingURL=_page.svelte-Bvpnlw8T.js.map
