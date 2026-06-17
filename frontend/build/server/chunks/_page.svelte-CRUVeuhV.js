import { c as create_ssr_component, a as subscribe, v as validate_component, d as add_attribute, f as escape } from './ssr-DDQ8otPt.js';
import './ssr2-CJcMdXvQ.js';
import './state.svelte-DYGtfCg5.js';
import { p as page } from './stores-vS07tqvC.js';
import { a as authStore } from './auth-CA0hEXLw.js';
import './index2-CqlzXTMx.js';
import { B as Button } from './Button-Da2PvDMC.js';
import { C as Card } from './Card-Cb1BEzwk.js';
import { I as Input } from './Input-CqhAj3_y.js';
import { A as Avatar } from './Avatar-DbEXgecQ.js';
import 'clsx';
import { T as Tabs } from './Tabs-CuVYs60O.js';
import { T as Textarea, S as Switch } from './Switch-CV-fn4et.js';
import { i as isAdmin } from './auth2-BoU0wlfj.js';
import './index-BCAmX91C.js';
import 'tailwind-merge';

const Page = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let adminUser;
  let $authStore, $$unsubscribe_authStore;
  let $page, $$unsubscribe_page;
  $$unsubscribe_authStore = subscribe(authStore, (value) => $authStore = value);
  $$unsubscribe_page = subscribe(page, (value) => $page = value);
  let loading = false;
  let activeTab = "profile";
  let siteName = "";
  let siteDescription = "";
  let platformFee = "";
  let withdrawalFee = "";
  let minWithdrawal = "";
  let minSubPrice = "";
  let maxSubPrice = "";
  let referralBonus = "";
  let maxUploadMb = "";
  let maintenanceMode = false;
  let registrationEnabled = true;
  let creatorVerificationRequired = false;
  let moneroEnabled = true;
  let btcpayEnabled = true;
  const tabs = [
    { id: "profile", label: "Profil" },
    { id: "subscription", label: "Abonelik" },
    { id: "privacy", label: "Gizlilik" },
    {
      id: "notifications",
      label: "Bildirimler"
    },
    { id: "security", label: "Güvenlik" }
  ];
  let displayName = "";
  let username = "";
  let bio = "";
  let location = "";
  let website = "";
  let subscriptionPrice = "";
  let showSubscribersCount = true;
  let allowMessages = true;
  let welcomeMessage = "";
  let showActivityStatus = true;
  let showOnlineStatus = true;
  let allowComments = true;
  let emailNotifications = true;
  let pushNotifications = true;
  let newSubscriberNotify = true;
  let newTipNotify = true;
  let newCommentNotify = true;
  let newMessageNotify = true;
  let currentPassword = "";
  let newPassword = "";
  let confirmPassword = "";
  let $$settled;
  let $$rendered;
  let previous_head = $$result.head;
  do {
    $$settled = true;
    $$result.head = previous_head;
    adminUser = isAdmin($authStore.user);
    {
      if ($page.url.searchParams.get("tab") === "site" && adminUser) {
        activeTab = "site";
      }
    }
    $$rendered = `${$$result.head += `<!-- HEAD_svelte-13d280r_START -->${$$result.title = `<title>Ayarlar | SadeceFanlar</title>`, ""}<!-- HEAD_svelte-13d280r_END -->`, ""} <div><h1 class="text-xl font-semibold mb-6" data-svelte-h="svelte-eo0lq8">Ayarlar</h1> ${validate_component(Tabs, "Tabs").$$render(
      $$result,
      {
        tabs: adminUser ? [...tabs, { id: "site", label: "Site Ayarları" }] : tabs,
        activeTab
      },
      {
        activeTab: ($$value) => {
          activeTab = $$value;
          $$settled = false;
        }
      },
      {
        default: () => {
          return `${activeTab === "profile" ? `${validate_component(Card, "Card").$$render($$result, { class: "p-6" }, {}, {
            default: () => {
              return `<form class="space-y-6"> <div class="space-y-4"><div><label class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2" data-svelte-h="svelte-2aqpsh">Profil Fotoğrafı</label> <div class="flex items-center gap-4">${validate_component(Avatar, "Avatar").$$render(
                $$result,
                {
                  src: $authStore.user?.avatar_url,
                  alt: displayName,
                  size: "lg"
                },
                {},
                {}
              )} <label class="cursor-pointer"><span class="text-sm text-primary hover:underline" data-svelte-h="svelte-l2m6hp">Fotoğrafı değiştir</span> <input type="file" accept="image/*" class="hidden"></label></div></div> <div><label class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2" data-svelte-h="svelte-kny4ee">Kapak Görseli</label> <div class="relative h-32 bg-neutral-100 dark:bg-neutral-800 rounded-lg overflow-hidden">${$authStore.user?.cover_url ? `<img${add_attribute(
                "src",
                $authStore.user?.cover_url,
                0
              )} alt="Cover" class="w-full h-full object-cover">` : ``} <label class="absolute inset-0 flex items-center justify-center bg-black/50 opacity-0 hover:opacity-100 transition-opacity cursor-pointer"><span class="text-white" data-svelte-h="svelte-19cbs7y">Kapağı değiştir</span> <input type="file" accept="image/*" class="hidden"></label></div></div></div> ${validate_component(Input, "Input").$$render(
                $$result,
                {
                  label: "Görünen Ad",
                  required: true,
                  value: displayName
                },
                {
                  value: ($$value) => {
                    displayName = $$value;
                    $$settled = false;
                  }
                },
                {}
              )} ${validate_component(Input, "Input").$$render(
                $$result,
                {
                  label: "Kullanıcı Adı",
                  value: username,
                  disabled: true
                },
                {},
                {}
              )} ${validate_component(Textarea, "Textarea").$$render(
                $$result,
                {
                  label: "Biyografi",
                  maxLength: 500,
                  rows: 4,
                  value: bio
                },
                {
                  value: ($$value) => {
                    bio = $$value;
                    $$settled = false;
                  }
                },
                {}
              )} ${validate_component(Input, "Input").$$render(
                $$result,
                {
                  label: "Konum",
                  placeholder: "Şehir, Ülke",
                  value: location
                },
                {
                  value: ($$value) => {
                    location = $$value;
                    $$settled = false;
                  }
                },
                {}
              )} ${validate_component(Input, "Input").$$render(
                $$result,
                {
                  label: "Web Sitesi",
                  type: "url",
                  placeholder: "https://",
                  value: website
                },
                {
                  value: ($$value) => {
                    website = $$value;
                    $$settled = false;
                  }
                },
                {}
              )} ${validate_component(Button, "Button").$$render($$result, { type: "submit", disabled: loading }, {}, {
                default: () => {
                  return `${escape("Değişiklikleri Kaydet")}`;
                }
              })}</form>`;
            }
          })}` : `${activeTab === "subscription" ? `${validate_component(Card, "Card").$$render($$result, { class: "p-6" }, {}, {
            default: () => {
              return `<form class="space-y-6">${validate_component(Input, "Input").$$render(
                $$result,
                {
                  type: "number",
                  label: "Aylık Abonelik Fiyatı ($)",
                  placeholder: "Ücretsiz için 0",
                  value: subscriptionPrice
                },
                {
                  value: ($$value) => {
                    subscriptionPrice = $$value;
                    $$settled = false;
                  }
                },
                {}
              )} <p class="text-xs text-neutral-500 -mt-4" data-svelte-h="svelte-1k2b0gt">Ücretsiz abonelik için 0 yazın. Platform %20 komisyon alır.</p> ${validate_component(Textarea, "Textarea").$$render(
                $$result,
                {
                  label: "Karşılama Mesajı",
                  placeholder: "Yeni abonelere gönderilen mesaj...",
                  rows: 3,
                  value: welcomeMessage
                },
                {
                  value: ($$value) => {
                    welcomeMessage = $$value;
                    $$settled = false;
                  }
                },
                {}
              )} <div class="space-y-4">${validate_component(Switch, "Switch").$$render(
                $$result,
                {
                  label: "Profilde abone sayısını göster",
                  checked: showSubscribersCount
                },
                {
                  checked: ($$value) => {
                    showSubscribersCount = $$value;
                    $$settled = false;
                  }
                },
                {}
              )} ${validate_component(Switch, "Switch").$$render(
                $$result,
                {
                  label: "Abonelerin mesaj göndermesine izin ver",
                  checked: allowMessages
                },
                {
                  checked: ($$value) => {
                    allowMessages = $$value;
                    $$settled = false;
                  }
                },
                {}
              )}</div> ${validate_component(Button, "Button").$$render($$result, { type: "submit", disabled: loading }, {}, {
                default: () => {
                  return `${escape("Ayarları Kaydet")}`;
                }
              })}</form>`;
            }
          })}` : `${activeTab === "privacy" ? `${validate_component(Card, "Card").$$render($$result, { class: "p-6" }, {}, {
            default: () => {
              return `<form class="space-y-6"><div class="space-y-4">${validate_component(Switch, "Switch").$$render(
                $$result,
                {
                  label: "Aktivite durumunu göster",
                  checked: showActivityStatus
                },
                {
                  checked: ($$value) => {
                    showActivityStatus = $$value;
                    $$settled = false;
                  }
                },
                {}
              )} ${validate_component(Switch, "Switch").$$render(
                $$result,
                {
                  label: "Çevrimiçi durumunu göster",
                  checked: showOnlineStatus
                },
                {
                  checked: ($$value) => {
                    showOnlineStatus = $$value;
                    $$settled = false;
                  }
                },
                {}
              )} ${validate_component(Switch, "Switch").$$render(
                $$result,
                {
                  label: "Gönderilere yorum yapılmasına izin ver",
                  checked: allowComments
                },
                {
                  checked: ($$value) => {
                    allowComments = $$value;
                    $$settled = false;
                  }
                },
                {}
              )}</div> ${validate_component(Button, "Button").$$render($$result, { type: "submit", disabled: loading }, {}, {
                default: () => {
                  return `${escape("Ayarları Kaydet")}`;
                }
              })}</form>`;
            }
          })}` : `${activeTab === "notifications" ? `${validate_component(Card, "Card").$$render($$result, { class: "p-6" }, {}, {
            default: () => {
              return `<form class="space-y-6"><div class="space-y-4"><h3 class="font-medium text-neutral-900 dark:text-white" data-svelte-h="svelte-1e95gn6">Kanallar</h3> ${validate_component(Switch, "Switch").$$render(
                $$result,
                {
                  label: "E-posta bildirimleri",
                  checked: emailNotifications
                },
                {
                  checked: ($$value) => {
                    emailNotifications = $$value;
                    $$settled = false;
                  }
                },
                {}
              )} ${validate_component(Switch, "Switch").$$render(
                $$result,
                {
                  label: "Anlık bildirimler",
                  checked: pushNotifications
                },
                {
                  checked: ($$value) => {
                    pushNotifications = $$value;
                    $$settled = false;
                  }
                },
                {}
              )}</div> <div class="space-y-4 pt-4 border-t border-neutral-200 dark:border-neutral-700"><h3 class="font-medium text-neutral-900 dark:text-white" data-svelte-h="svelte-x9sia">Olaylar</h3> ${validate_component(Switch, "Switch").$$render(
                $$result,
                {
                  label: "Yeni abone",
                  checked: newSubscriberNotify
                },
                {
                  checked: ($$value) => {
                    newSubscriberNotify = $$value;
                    $$settled = false;
                  }
                },
                {}
              )} ${validate_component(Switch, "Switch").$$render(
                $$result,
                {
                  label: "Yeni bahşiş alındı",
                  checked: newTipNotify
                },
                {
                  checked: ($$value) => {
                    newTipNotify = $$value;
                    $$settled = false;
                  }
                },
                {}
              )} ${validate_component(Switch, "Switch").$$render(
                $$result,
                {
                  label: "Yeni yorum",
                  checked: newCommentNotify
                },
                {
                  checked: ($$value) => {
                    newCommentNotify = $$value;
                    $$settled = false;
                  }
                },
                {}
              )} ${validate_component(Switch, "Switch").$$render(
                $$result,
                {
                  label: "Yeni mesaj",
                  checked: newMessageNotify
                },
                {
                  checked: ($$value) => {
                    newMessageNotify = $$value;
                    $$settled = false;
                  }
                },
                {}
              )}</div> ${validate_component(Button, "Button").$$render($$result, { type: "submit", disabled: loading }, {}, {
                default: () => {
                  return `${escape("Ayarları Kaydet")}`;
                }
              })}</form>`;
            }
          })}` : `${activeTab === "security" ? `<div class="space-y-6">${validate_component(Card, "Card").$$render($$result, { class: "p-6" }, {}, {
            default: () => {
              return `<h3 class="font-medium text-neutral-900 dark:text-white mb-4" data-svelte-h="svelte-8cr5sf">Şifre Değiştir</h3> <form class="space-y-4">${validate_component(Input, "Input").$$render(
                $$result,
                {
                  type: "password",
                  label: "Mevcut Şifre",
                  required: true,
                  value: currentPassword
                },
                {
                  value: ($$value) => {
                    currentPassword = $$value;
                    $$settled = false;
                  }
                },
                {}
              )} ${validate_component(Input, "Input").$$render(
                $$result,
                {
                  type: "password",
                  label: "Yeni Şifre",
                  required: true,
                  value: newPassword
                },
                {
                  value: ($$value) => {
                    newPassword = $$value;
                    $$settled = false;
                  }
                },
                {}
              )} ${validate_component(Input, "Input").$$render(
                $$result,
                {
                  type: "password",
                  label: "Yeni Şifre Tekrar",
                  required: true,
                  value: confirmPassword
                },
                {
                  value: ($$value) => {
                    confirmPassword = $$value;
                    $$settled = false;
                  }
                },
                {}
              )} ${validate_component(Button, "Button").$$render($$result, { type: "submit", disabled: loading }, {}, {
                default: () => {
                  return `${escape("Şifreyi Değiştir")}`;
                }
              })}</form>`;
            }
          })} ${validate_component(Card, "Card").$$render($$result, { class: "p-6" }, {}, {
            default: () => {
              return `<h3 class="font-medium text-neutral-900 dark:text-white mb-4" data-svelte-h="svelte-3ytork">İki Faktörlü Doğrulama</h3> <p class="text-sm text-neutral-500 mb-4" data-svelte-h="svelte-1da67ad">Doğrulama uygulaması kullanarak hesabınıza ekstra güvenlik katın.</p> <div class="flex items-center justify-between"><div><p class="font-medium text-neutral-900 dark:text-white">${escape("2FA Kapalı")}</p> <p class="text-sm text-neutral-500">${escape("Daha iyi güvenlik için etkinleştirin")}</p></div> ${validate_component(Button, "Button").$$render(
                $$result,
                {
                  variant: "default",
                  disabled: loading
                },
                {},
                {
                  default: () => {
                    return `${escape("Etkinleştir")}`;
                  }
                }
              )}</div>`;
            }
          })} ${validate_component(Card, "Card").$$render(
            $$result,
            {
              class: "p-6 border-red-200 dark:border-red-800"
            },
            {},
            {
              default: () => {
                return `<h3 class="font-medium text-red-600 mb-4" data-svelte-h="svelte-1sa2oex">Tehlikeli Bölge</h3> <p class="text-sm text-neutral-500 mb-4" data-svelte-h="svelte-3dvbcq">Hesabınızı sildiğinizde geri dönüş yoktur. Lütfen emin olun.</p> ${validate_component(Button, "Button").$$render($$result, { variant: "danger" }, {}, {
                  default: () => {
                    return `Hesabı Sil`;
                  }
                })}`;
              }
            }
          )}</div>` : `${activeTab === "site" && adminUser ? `<div class="space-y-4">${validate_component(Card, "Card").$$render($$result, { class: "p-6" }, {}, {
            default: () => {
              return `<h3 class="font-medium mb-4" data-svelte-h="svelte-ckrug9">Genel</h3> <form class="space-y-4">${validate_component(Input, "Input").$$render(
                $$result,
                { label: "Site adı", value: siteName },
                {
                  value: ($$value) => {
                    siteName = $$value;
                    $$settled = false;
                  }
                },
                {}
              )} ${validate_component(Textarea, "Textarea").$$render(
                $$result,
                {
                  label: "Site açıklaması",
                  rows: 3,
                  value: siteDescription
                },
                {
                  value: ($$value) => {
                    siteDescription = $$value;
                    $$settled = false;
                  }
                },
                {}
              )} <div class="grid grid-cols-1 md:grid-cols-2 gap-4">${validate_component(Input, "Input").$$render(
                $$result,
                {
                  label: "Platform komisyonu (%)",
                  type: "number",
                  value: platformFee
                },
                {
                  value: ($$value) => {
                    platformFee = $$value;
                    $$settled = false;
                  }
                },
                {}
              )} ${validate_component(Input, "Input").$$render(
                $$result,
                {
                  label: "Çekim ücreti (%)",
                  type: "number",
                  value: withdrawalFee
                },
                {
                  value: ($$value) => {
                    withdrawalFee = $$value;
                    $$settled = false;
                  }
                },
                {}
              )} ${validate_component(Input, "Input").$$render(
                $$result,
                {
                  label: "Min. çekim ($)",
                  type: "number",
                  value: minWithdrawal
                },
                {
                  value: ($$value) => {
                    minWithdrawal = $$value;
                    $$settled = false;
                  }
                },
                {}
              )} ${validate_component(Input, "Input").$$render(
                $$result,
                {
                  label: "Min. abonelik ($)",
                  type: "number",
                  value: minSubPrice
                },
                {
                  value: ($$value) => {
                    minSubPrice = $$value;
                    $$settled = false;
                  }
                },
                {}
              )} ${validate_component(Input, "Input").$$render(
                $$result,
                {
                  label: "Max. abonelik ($)",
                  type: "number",
                  value: maxSubPrice
                },
                {
                  value: ($$value) => {
                    maxSubPrice = $$value;
                    $$settled = false;
                  }
                },
                {}
              )} ${validate_component(Input, "Input").$$render(
                $$result,
                {
                  label: "Referans bonusu (%)",
                  type: "number",
                  value: referralBonus
                },
                {
                  value: ($$value) => {
                    referralBonus = $$value;
                    $$settled = false;
                  }
                },
                {}
              )} ${validate_component(Input, "Input").$$render(
                $$result,
                {
                  label: "Max. yükleme (MB)",
                  type: "number",
                  value: maxUploadMb
                },
                {
                  value: ($$value) => {
                    maxUploadMb = $$value;
                    $$settled = false;
                  }
                },
                {}
              )}</div> <div class="space-y-3 pt-2">${validate_component(Switch, "Switch").$$render(
                $$result,
                {
                  label: "Bakım modu",
                  checked: maintenanceMode
                },
                {
                  checked: ($$value) => {
                    maintenanceMode = $$value;
                    $$settled = false;
                  }
                },
                {}
              )} ${validate_component(Switch, "Switch").$$render(
                $$result,
                {
                  label: "Kayıt açık",
                  checked: registrationEnabled
                },
                {
                  checked: ($$value) => {
                    registrationEnabled = $$value;
                    $$settled = false;
                  }
                },
                {}
              )} ${validate_component(Switch, "Switch").$$render(
                $$result,
                {
                  label: "Üretici onayı zorunlu",
                  checked: creatorVerificationRequired
                },
                {
                  checked: ($$value) => {
                    creatorVerificationRequired = $$value;
                    $$settled = false;
                  }
                },
                {}
              )} ${validate_component(Switch, "Switch").$$render(
                $$result,
                {
                  label: "Monero ödemeleri",
                  checked: moneroEnabled
                },
                {
                  checked: ($$value) => {
                    moneroEnabled = $$value;
                    $$settled = false;
                  }
                },
                {}
              )} ${validate_component(Switch, "Switch").$$render(
                $$result,
                {
                  label: "Bitcoin (BTCPay) ödemeleri",
                  checked: btcpayEnabled
                },
                {
                  checked: ($$value) => {
                    btcpayEnabled = $$value;
                    $$settled = false;
                  }
                },
                {}
              )}</div> ${validate_component(Button, "Button").$$render($$result, { type: "submit", disabled: loading }, {}, {
                default: () => {
                  return `Kaydet`;
                }
              })}</form>`;
            }
          })}</div>` : ``}`}`}`}`}`}`;
        }
      }
    )}</div>`;
  } while (!$$settled);
  $$unsubscribe_authStore();
  $$unsubscribe_page();
  return $$rendered;
});

export { Page as default };
//# sourceMappingURL=_page.svelte-CRUVeuhV.js.map
