import { c as create_ssr_component, d as add_attribute, f as escape } from './ssr-DDQ8otPt.js';
import { c as cn } from './index2-BnafdvHM.js';

const Avatar = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let initials;
  let { src = void 0 } = $$props;
  let { alt = "" } = $$props;
  let { fallback = "" } = $$props;
  let { size = "md" } = $$props;
  let { class: className = "" } = $$props;
  const sizes = {
    sm: "h-8 w-8",
    md: "h-10 w-10",
    lg: "h-16 w-16",
    xl: "h-24 w-24"
  };
  if ($$props.src === void 0 && $$bindings.src && src !== void 0) $$bindings.src(src);
  if ($$props.alt === void 0 && $$bindings.alt && alt !== void 0) $$bindings.alt(alt);
  if ($$props.fallback === void 0 && $$bindings.fallback && fallback !== void 0) $$bindings.fallback(fallback);
  if ($$props.size === void 0 && $$bindings.size && size !== void 0) $$bindings.size(size);
  if ($$props.class === void 0 && $$bindings.class && className !== void 0) $$bindings.class(className);
  initials = fallback || alt?.charAt(0)?.toUpperCase() || "?";
  return `<div${add_attribute("class", cn("relative flex shrink-0 overflow-hidden rounded-full bg-muted", sizes[size], className), 0)}>${src && true ? `<img${add_attribute("src", src, 0)}${add_attribute("alt", alt, 0)} class="aspect-square h-full w-full object-cover">` : `<span class="flex h-full w-full items-center justify-center bg-gradient-to-br from-primary to-accent text-sm font-medium text-white">${escape(initials)}</span>`}</div>`;
});

export { Avatar as A };
//# sourceMappingURL=Avatar-CJBrCmrS.js.map
