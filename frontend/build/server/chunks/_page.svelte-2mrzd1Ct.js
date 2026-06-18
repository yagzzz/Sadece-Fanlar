import { c as create_ssr_component, v as validate_component, e as each } from './ssr-DDQ8otPt.js';
import './index2-DIqK_D2c.js';
import 'clsx';
import { I as Input } from './Input-DHAIDfxf.js';
import { S as Skeleton } from './Skeleton-1_Puv0XT.js';
import { T as Tabs } from './Tabs-D9Dk_Bep.js';
import './auth-C_KGpDdi.js';
import 'tailwind-merge';
import './index-BCAmX91C.js';

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
    $$rendered = `${$$result.head += `<!-- HEAD_svelte-1y54knw_START -->${$$result.title = `<title>İçerik Üreticilerini Keşfet | SadeceFanlar</title>`, ""}<!-- HEAD_svelte-1y54knw_END -->`, ""} <div class="space-y-5"><h1 class="text-xl font-semibold text-neutral-900 dark:text-white" data-svelte-h="svelte-trvm5o">Keşfet</h1>  ${validate_component(Input, "Input").$$render(
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
//# sourceMappingURL=_page.svelte-2mrzd1Ct.js.map
