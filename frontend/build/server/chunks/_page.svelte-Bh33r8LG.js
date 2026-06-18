import { c as create_ssr_component, a as subscribe, v as validate_component, e as each, f as escape, d as add_attribute } from './ssr-DDQ8otPt.js';
import './ssr2-CJcMdXvQ.js';
import './state.svelte-DYGtfCg5.js';
import { a as authStore } from './auth-C_KGpDdi.js';
import './index2-DIqK_D2c.js';
import { B as Button } from './Button-DeTt_asi.js';
import { C as Card } from './Card-BxCPRD7E.js';
import { I as Input } from './Input-DHAIDfxf.js';
import 'clsx';
import { T as Textarea, S as Switch } from './Switch-DadwRrB-.js';
import './index-BCAmX91C.js';
import 'tailwind-merge';

const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let $$unsubscribe_authStore;
  $$unsubscribe_authStore = subscribe(authStore, (value) => value);
  let content = "";
  let price = "";
  let isPremium = false;
  let scheduledAt = "";
  let mediaFiles = [];
  let mediaPreviews = [];
  let $$settled;
  let $$rendered;
  let previous_head = $$result.head;
  do {
    $$settled = true;
    $$result.head = previous_head;
    $$rendered = `${$$result.head += `<!-- HEAD_svelte-dud9ep_START -->${$$result.title = `<title>Yeni Gönderi | SadeceFanlar</title>`, ""}<!-- HEAD_svelte-dud9ep_END -->`, ""} <div class="p-4 max-w-2xl mx-auto"><div class="flex items-center justify-between mb-6"><h1 class="text-2xl font-bold text-neutral-900 dark:text-white" data-svelte-h="svelte-zx7yrx">Gönderi Oluştur</h1> ${validate_component(Button, "Button").$$render($$result, { variant: "ghost", href: "/" }, {}, {
      default: () => {
        return `İptal`;
      }
    })}</div> ${validate_component(Card, "Card").$$render($$result, { class: "p-6" }, {}, {
      default: () => {
        return `<form class="space-y-6">${validate_component(Textarea, "Textarea").$$render(
          $$result,
          {
            placeholder: "Aklınızdan ne geçiyor?",
            rows: 6,
            maxLength: 5e3,
            value: content
          },
          {
            value: ($$value) => {
              content = $$value;
              $$settled = false;
            }
          },
          {}
        )}  <div><label class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2" data-svelte-h="svelte-wsgt4l">Medya (isteğe bağlı)</label> ${mediaPreviews.length > 0 ? `<div class="grid grid-cols-3 gap-2 mb-4">${each(mediaPreviews, (preview, i) => {
          return `<div class="relative aspect-square rounded-lg overflow-hidden bg-neutral-100 dark:bg-neutral-800">${mediaFiles[i]?.type.startsWith("video/") ? `<video${add_attribute("src", preview, 0)} class="w-full h-full object-cover"><track kind="captions"></video>` : `<img${add_attribute("src", preview, 0)} alt="Preview" class="w-full h-full object-cover">`} <button type="button" class="absolute top-1 right-1 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-sm hover:bg-red-600 transition-colors" data-svelte-h="svelte-1htyvug">×</button> </div>`;
        })}</div>` : ``} <label class="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-neutral-300 dark:border-neutral-600 rounded-lg cursor-pointer hover:border-primary transition-colors"><div class="flex flex-col items-center justify-center pt-5 pb-6" data-svelte-h="svelte-62w0xa"><span class="text-3xl mb-2">📷</span> <p class="text-sm text-neutral-500">Fotoğraf veya video yüklemek için tıklayın</p> <p class="text-xs text-neutral-400">PNG, JPG, GIF, MP4 maksimum 100MB</p></div> <input type="file" accept="image/*,video/*" multiple class="hidden"></label></div>  <div class="space-y-4 p-4 bg-neutral-50 dark:bg-neutral-800 rounded-lg">${validate_component(Switch, "Switch").$$render(
          $$result,
          {
            label: "Premium İçerik (İzle başına öde)",
            checked: isPremium
          },
          {
            checked: ($$value) => {
              isPremium = $$value;
              $$settled = false;
            }
          },
          {}
        )} ${isPremium ? `${validate_component(Input, "Input").$$render(
          $$result,
          {
            type: "number",
            label: "Fiyat ($)",
            placeholder: "0.00",
            min: "0",
            step: "0.01",
            value: price
          },
          {
            value: ($$value) => {
              price = $$value;
              $$settled = false;
            }
          },
          {}
        )} <p class="text-xs text-neutral-500" data-svelte-h="svelte-yqlq3n">Sadece aboneler veya ödeme yapan kullanıcılar bu içeriği görebilir.
						Abone olmayanlar bulanık bir önizleme görür.</p>` : ``}</div>  <div>${validate_component(Input, "Input").$$render(
          $$result,
          {
            type: "datetime-local",
            label: "Gönderiyi Zamanla (isteğe bağlı)",
            value: scheduledAt
          },
          {
            value: ($$value) => {
              scheduledAt = $$value;
              $$settled = false;
            }
          },
          {}
        )}</div>  ${``}  <div class="flex gap-2">${validate_component(Button, "Button").$$render(
          $$result,
          {
            type: "submit",
            class: "flex-1",
            disabled: !content && mediaFiles.length === 0
          },
          {},
          {
            default: () => {
              return `${escape(scheduledAt ? "Gönderiyi Zamanla" : "Şimdi Paylaş")}`;
            }
          }
        )}</div></form>`;
      }
    })}</div>`;
  } while (!$$settled);
  $$unsubscribe_authStore();
  return $$rendered;
});

export { Page as default };
//# sourceMappingURL=_page.svelte-Bh33r8LG.js.map
