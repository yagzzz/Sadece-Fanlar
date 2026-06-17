import { c as create_ssr_component, v as validate_component } from './ssr-CAqK4lyn.js';
import './index2-O1tI1Vis.js';
import 'clsx';
import { S as Spinner } from './Spinner-BW-cLHP2.js';
import './auth-DjJDNFfu.js';
import 'tailwind-merge';
import './index-BTslQZ0_.js';

const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let $$settled;
  let $$rendered;
  let previous_head = $$result.head;
  do {
    $$settled = true;
    $$result.head = previous_head;
    $$rendered = `${$$result.head += `<!-- HEAD_svelte-vbs8zv_START -->${$$result.title = `<title>Cüzdan | SadeceFanlar</title>`, ""}<!-- HEAD_svelte-vbs8zv_END -->`, ""} <div class="p-4"><h1 class="text-2xl font-bold text-neutral-900 dark:text-white mb-6" data-svelte-h="svelte-q7ztns">Cüzdan</h1> ${`<div class="flex items-center justify-center py-12">${validate_component(Spinner, "Spinner").$$render($$result, { size: "lg" }, {}, {})}</div>`}</div>`;
  } while (!$$settled);
  return $$rendered;
});

export { Page as default };
//# sourceMappingURL=_page.svelte-BlBuSdm4.js.map
