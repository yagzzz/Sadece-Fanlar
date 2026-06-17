import { c as create_ssr_component, l as compute_rest_props, p as spread, q as escape_attribute_value, t as escape_object } from './ssr-CAqK4lyn.js';
import { c as cn } from './index2-O1tI1Vis.js';

const Button = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let $$restProps = compute_rest_props($$props, ["variant", "size", "disabled", "loading", "type", "href", "class"]);
  let { variant = "default" } = $$props;
  let { size = "md" } = $$props;
  let { disabled = false } = $$props;
  let { loading = false } = $$props;
  let { type = "button" } = $$props;
  let { href = void 0 } = $$props;
  let { class: className = "" } = $$props;
  const variants = {
    default: "bg-primary text-white hover:bg-primary/90",
    secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
    outline: "border border-input bg-transparent hover:bg-accent hover:text-accent-foreground",
    ghost: "hover:bg-accent hover:text-accent-foreground",
    danger: "bg-destructive text-destructive-foreground hover:bg-destructive/90"
  };
  const sizes = {
    sm: "h-8 px-3 text-xs",
    md: "h-10 px-4 py-2",
    lg: "h-12 px-6 text-lg",
    icon: "h-10 w-10"
  };
  if ($$props.variant === void 0 && $$bindings.variant && variant !== void 0) $$bindings.variant(variant);
  if ($$props.size === void 0 && $$bindings.size && size !== void 0) $$bindings.size(size);
  if ($$props.disabled === void 0 && $$bindings.disabled && disabled !== void 0) $$bindings.disabled(disabled);
  if ($$props.loading === void 0 && $$bindings.loading && loading !== void 0) $$bindings.loading(loading);
  if ($$props.type === void 0 && $$bindings.type && type !== void 0) $$bindings.type(type);
  if ($$props.href === void 0 && $$bindings.href && href !== void 0) $$bindings.href(href);
  if ($$props.class === void 0 && $$bindings.class && className !== void 0) $$bindings.class(className);
  return `${href && !disabled ? `<a${spread(
    [
      { href: escape_attribute_value(href) },
      {
        class: escape_attribute_value(cn("inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors", "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring", variants[variant], sizes[size], className))
      },
      escape_object($$restProps)
    ],
    {}
  )}>${slots.default ? slots.default({}) : ``}</a>` : `<button${spread(
    [
      { type: escape_attribute_value(type) },
      { disabled: disabled || loading || null },
      {
        class: escape_attribute_value(cn("inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors", "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring", "disabled:pointer-events-none disabled:opacity-50", variants[variant], sizes[size], className))
      },
      escape_object($$restProps)
    ],
    {}
  )}>${loading ? `<svg class="h-4 w-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>` : ``} ${slots.default ? slots.default({}) : ``}</button>`}`;
});

export { Button as B };
//# sourceMappingURL=Button-DYjEXmaK.js.map
