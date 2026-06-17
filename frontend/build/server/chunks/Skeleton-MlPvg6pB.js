import { c as create_ssr_component, d as add_attribute, g as add_styles, e as each } from './ssr-CAqK4lyn.js';
import { c as cn } from './index2-O1tI1Vis.js';

const baseClass = "animate-pulse bg-neutral-200 dark:bg-neutral-700 rounded";
const Skeleton = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { variant = "text" } = $$props;
  let { width = void 0 } = $$props;
  let { height = void 0 } = $$props;
  let { lines = 1 } = $$props;
  let { class: className = "" } = $$props;
  if ($$props.variant === void 0 && $$bindings.variant && variant !== void 0) $$bindings.variant(variant);
  if ($$props.width === void 0 && $$bindings.width && width !== void 0) $$bindings.width(width);
  if ($$props.height === void 0 && $$bindings.height && height !== void 0) $$bindings.height(height);
  if ($$props.lines === void 0 && $$bindings.lines && lines !== void 0) $$bindings.lines(lines);
  if ($$props.class === void 0 && $$bindings.class && className !== void 0) $$bindings.class(className);
  return `${variant === "circular" ? `<div${add_attribute("class", cn(baseClass, "rounded-full", className), 0)}${add_styles({
    "width": width || "40px",
    "height": height || "40px"
  })}></div>` : `${variant === "rectangular" ? `<div${add_attribute("class", cn(baseClass, className), 0)}${add_styles({
    "width": width || "100%",
    "height": height || "100px"
  })}></div>` : `<div${add_attribute("class", cn("space-y-2", className), 0)}>${each(Array(lines), (_, i) => {
    return `<div${add_attribute("class", cn(baseClass, "h-4"), 0)}${add_styles({
      "width": i === lines - 1 && lines > 1 ? "60%" : width || "100%"
    })}></div>`;
  })}</div>`}`}`;
});

export { Skeleton as S };
//# sourceMappingURL=Skeleton-MlPvg6pB.js.map
