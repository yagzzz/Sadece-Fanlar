import { c as create_ssr_component, a as subscribe, v as validate_component } from './ssr-CxJiF8w8.js';
import './ssr2-CJcMdXvQ.js';
import './state.svelte-DYGtfCg5.js';
import { a as authStore } from './auth-BhyVnWr0.js';
import './client-CybrWH6X.js';
import 'clsx';
import { S as Spinner } from './Spinner-DnO2KtYq.js';
import './index-YI0dIwkT.js';
import './index2-Dhq654YE.js';
import 'tailwind-merge';

const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let $$unsubscribe_authStore;
  $$unsubscribe_authStore = subscribe(authStore, (value) => value);
  let $$settled;
  let $$rendered;
  let previous_head = $$result.head;
  do {
    $$settled = true;
    $$result.head = previous_head;
    $$rendered = `${$$result.head += `<!-- HEAD_svelte-vbs8zv_START -->${$$result.title = `<title>Cüzdan | SadeceFanlar</title>`, ""}<!-- HEAD_svelte-vbs8zv_END -->`, ""} <div><h1 class="text-xl font-semibold mb-6" data-svelte-h="svelte-15iiooo">Cüzdan</h1> ${`<div class="flex items-center justify-center py-12">${validate_component(Spinner, "Spinner").$$render($$result, { size: "lg" }, {}, {})}</div>`}</div>`;
  } while (!$$settled);
  $$unsubscribe_authStore();
  return $$rendered;
});

export { Page as default };
//# sourceMappingURL=_page.svelte-BdKi-5Kb.js.map
