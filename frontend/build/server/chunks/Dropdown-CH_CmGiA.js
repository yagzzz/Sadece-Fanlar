import { c as create_ssr_component, b as createEventDispatcher, d as add_attribute } from './ssr-CAqK4lyn.js';
import { c as cn } from './index2-O1tI1Vis.js';

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

export { Dropdown as D };
//# sourceMappingURL=Dropdown-CH_CmGiA.js.map
