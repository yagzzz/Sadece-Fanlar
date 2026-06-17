import { c as create_ssr_component, o as onDestroy, d as add_attribute, e as each, v as validate_component } from './ssr-DDQ8otPt.js';
import { c as cn } from './index2-CqlzXTMx.js';
import './auth-CA0hEXLw.js';
import { S as Skeleton } from './Skeleton-O_8fOjCX.js';
import 'clsx';
import 'tailwind-merge';
import './index-BCAmX91C.js';

const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let selectedConversation = null;
  onDestroy(() => {
  });
  return `${$$result.head += `<!-- HEAD_svelte-qb2rjm_START -->${$$result.title = `<title>Mesajlar | SadeceFanlar</title>`, ""}<!-- HEAD_svelte-qb2rjm_END -->`, ""} <div class="flex h-[calc(100vh-4rem)] lg:h-screen"> <div${add_attribute("class", cn("w-full md:w-80 border-r border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 flex flex-col", selectedConversation), 0)}><div class="p-4 border-b border-neutral-200 dark:border-neutral-800" data-svelte-h="svelte-6mf7jy"><h1 class="text-xl font-bold text-neutral-900 dark:text-white">Mesajlar</h1></div> <div class="flex-1 overflow-y-auto">${`${each(Array(5), (_) => {
    return `<div class="flex items-center gap-3 p-4 border-b border-neutral-100 dark:border-neutral-800">${validate_component(Skeleton, "Skeleton").$$render(
      $$result,
      {
        variant: "circular",
        width: "48px",
        height: "48px"
      },
      {},
      {}
    )} <div class="flex-1">${validate_component(Skeleton, "Skeleton").$$render($$result, { width: "60%" }, {}, {})} ${validate_component(Skeleton, "Skeleton").$$render($$result, { width: "80%", class: "mt-1" }, {}, {})}</div> </div>`;
  })}`}</div></div>  <div${add_attribute("class", cn("flex-1 flex flex-col bg-neutral-50 dark:bg-neutral-950", "hidden md:flex"), 0)}>${` <div class="flex-1 flex items-center justify-center" data-svelte-h="svelte-c8m3dq"><div class="text-center"><p class="text-6xl mb-4">💬</p> <p class="text-neutral-500">Mesajlaşmaya başlamak için bir sohbet seçin</p></div></div>`}</div></div>`;
});

export { Page as default };
//# sourceMappingURL=_page.svelte-CY3KGnU9.js.map
