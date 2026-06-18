import { c as create_ssr_component, d as add_attribute, e as each, f as escape } from './ssr-CxJiF8w8.js';
import './client-DAdgJWpw.js';

const AdSlot = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let { position } = $$props;
  let { vertical = false } = $$props;
  let { class: className = "" } = $$props;
  let ads = [];
  if ($$props.position === void 0 && $$bindings.position && position !== void 0) $$bindings.position(position);
  if ($$props.vertical === void 0 && $$bindings.vertical && vertical !== void 0) $$bindings.vertical(vertical);
  if ($$props.class === void 0 && $$bindings.class && className !== void 0) $$bindings.class(className);
  return `${ads.length > 0 ? `<div${add_attribute("class", className, 0)}>${each(ads, (ad) => {
    return `<div class="${"relative overflow-hidden rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 cursor-pointer " + escape(vertical ? "mb-4" : "mb-4", true)}" role="button" tabindex="0"> <span class="absolute top-2 right-2 z-10 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide rounded bg-yellow-400 text-black shadow" data-svelte-h="svelte-tncp70">Reklam</span> ${ad.content_html ? `<!-- HTML_TAG_START -->${ad.content_html}<!-- HTML_TAG_END -->` : `${ad.image_url && (ad.image_url.endsWith(".mp4") || ad.image_url.endsWith(".webm")) ? `<video${add_attribute("src", ad.image_url, 0)} autoplay muted loop playsinline class="${"w-full " + escape(vertical ? "h-96 object-cover" : "h-auto", true)}"></video>` : `${ad.image_url ? `<img${add_attribute("src", ad.image_url, 0)}${add_attribute("alt", ad.name, 0)} class="${"w-full " + escape(vertical ? "h-96 object-cover" : "h-auto", true)}">` : `<div class="p-6 text-center text-sm text-neutral-500">${escape(ad.name)}</div>`}`}`} </div>`;
  })}</div>` : ``}`;
});

export { AdSlot as A };
//# sourceMappingURL=AdSlot-fj2CHqgD.js.map
