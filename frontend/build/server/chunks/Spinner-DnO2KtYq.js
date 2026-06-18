import { c as create_ssr_component, d as add_attribute } from './ssr-CxJiF8w8.js';
import { c as cn } from './index2-Dhq654YE.js';

const Spinner = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { size = "md" } = $$props;
  let { class: className = "" } = $$props;
  const sizes = {
    sm: "h-4 w-4",
    md: "h-6 w-6",
    lg: "h-8 w-8"
  };
  if ($$props.size === void 0 && $$bindings.size && size !== void 0) $$bindings.size(size);
  if ($$props.class === void 0 && $$bindings.class && className !== void 0) $$bindings.class(className);
  return `<svg${add_attribute("class", cn("animate-spin text-primary", sizes[size], className), 0)} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>`;
});

export { Spinner as S };
//# sourceMappingURL=Spinner-DnO2KtYq.js.map
