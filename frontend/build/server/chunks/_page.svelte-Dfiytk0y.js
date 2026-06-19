import { c as create_ssr_component, a as subscribe, v as validate_component } from './ssr-CxJiF8w8.js';
import './ssr2-CJcMdXvQ.js';
import './state.svelte-DYGtfCg5.js';
import { a as authStore } from './auth-BhyVnWr0.js';
import './client-CybrWH6X.js';
import { B as Button } from './Button-ClLhbrma.js';
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
    $$rendered = `${$$result.head += `<!-- HEAD_svelte-170pvlm_START -->${$$result.title = `<title>Destek | SadeceFanlar</title>`, ""}<!-- HEAD_svelte-170pvlm_END -->`, ""} <div><div class="flex items-center justify-between mb-6"><h1 class="text-xl font-semibold" data-svelte-h="svelte-xy59no">Destek</h1> ${validate_component(Button, "Button").$$render($$result, { size: "sm" }, {}, {
      default: () => {
        return `Yeni Talep`;
      }
    })}</div> ${``} ${`${`<div class="flex justify-center py-12">${validate_component(Spinner, "Spinner").$$render($$result, { size: "lg" }, {}, {})}</div>`}`}</div>`;
  } while (!$$settled);
  $$unsubscribe_authStore();
  return $$rendered;
});

export { Page as default };
//# sourceMappingURL=_page.svelte-Dfiytk0y.js.map
