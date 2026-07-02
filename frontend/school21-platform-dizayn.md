# 21-School Platform — Dizayn Tizimi (Design System)

> Bu hujjat ochiq manbalarda topilgan skrinshotlar (Dashboard va Calendar sahifalari) asosida tahlil qilingan. Rang kodlari skrinshotlardan vizual taxmin qilingan — agar to'liq aniqlik kerak bo'lsa, o'zingiz platformaga kirib, brauzer DevTools (Inspect Element) orqali aniq HEX kodlarini va shrift nomini tekshirib oling. Bu hujjat sizga **boshlang'ich nuqta va tizim** sifatida xizmat qiladi.

---

## 1. Umumiy konsepsiya

Platform — **dark mode (qorong'i tema)** asosida qurilgan, minimalistik, lekin "o'yinlashtirilgan" (gamification) elementlarga boy ta'lim platformasi. Asosiy xarakteristikalari:

- Qora-ko'k fon (deep navy), ustida och rangli (oq/kulrang) matn
- Yorqin **teal/yashil-firuza** va **ko'k** aksent ranglar — progress, tugmalar, havolalar uchun
- Yumaloq burchaklar (rounded corners) — barcha kartalar, tugmalar, inputlarda
- Geometrik, "blob" shaklidagi gradient dekorativ shakllar — fon bezagi sifatida
- Gamifikatsiya elementlari: level, progress bar, coin, ball (point) ko'rsatkichlari

---

## 2. Rang palitrasi (Color Palette)

### Fon ranglari
| Nomi | HEX (taxminiy) | Qo'llanilishi |
|---|---|---|
| Background (asosiy) | `#171B26` | Sahifa umumiy foni |
| Surface / Card | `#1E2330` | Kartalar, modal oynalar foni |
| Border / Divider | `#2A3040` | Ajratuvchi chiziqlar, grid liniyalari |
| Input background | `#2B3142` | Search bar, input maydonlar |

### Aksent ranglar
| Nomi | HEX (taxminiy) | Qo'llanilishi |
|---|---|---|
| Teal / Firuza (asosiy brend rangi) | `#2DD9C5` | Logotip, progress bar gradienti |
| Yashil (Success/CTA) | `#3DDC84` | Asosiy tugmalar (masalan "Copy slug!"), faol nav tab chizig'i |
| Ko'k (Info/Link) | `#3B82F6` | Kalendar event kartalari, havolalar (link) |
| Binafsha (Highlight) | `#8B5CF6` | Foydalanuvchi nikneymi, maxsus belgilash |

### Matn ranglari
| Nomi | HEX (taxminiy) | Qo'llanilishi |
|---|---|---|
| Asosiy matn | `#FFFFFF` / `#F3F4F6` | Sarlavhalar, asosiy matn |
| Ikkilamchi matn | `#9CA3AF` | Yordamchi matn, label'lar, placeholder |
| Muted / Disabled | `#6B7280` | Faol bo'lmagan nav elementlar |

> **Maslahat:** CSS'da bu ranglarni o'zgaruvchi (variable) sifatida belgilang, masalan `--bg-primary`, `--accent-teal`, `--accent-green` va h.k. — shunda butun loyiha bo'ylab izchillikni saqlash oson bo'ladi.

```css
:root {
  --bg-primary: #171B26;
  --bg-surface: #1E2330;
  --border-color: #2A3040;
  --input-bg: #2B3142;

  --accent-teal: #2DD9C5;
  --accent-green: #3DDC84;
  --accent-blue: #3B82F6;
  --accent-purple: #8B5CF6;

  --text-primary: #FFFFFF;
  --text-secondary: #9CA3AF;
  --text-muted: #6B7280;
}
```

---

## 3. Tipografiya (Typography)

- **Shrift oilasi:** Zamonaviy, geometrik sans-serif (`Inter`, `Manrope` yoki `SF Pro Display` uslubiga juda yaqin). Tavsiya: Google Fonts'dan **Inter** ishlatish (bepul va o'xshash).
- **Sarlavhalar (Headings):** Bold (600–700 og'irlik), masalan "Participant Peer Review" — ~28–32px
- **Nav menyu matni:** Medium (500), ~16px
- **Asosiy matn (body):** Regular (400), ~14–16px
- **Yordamchi matn (label, sana):** Regular, kichikroq (~13–14px), kulrang rangda

```css
body {
  font-family: 'Inter', -apple-system, sans-serif;
}
h1, h2, .title { font-weight: 700; }
.nav-item { font-weight: 500; }
.label-text { font-weight: 400; color: var(--text-secondary); }
```

---

## 4. Layout va asosiy komponentlar

### 4.1 Top Navigation Bar
- Chap tomonda: logotip (yumaloq burchakli kvadrat ichida, gradient teal fon)
- O'rtada: gorizontal menyu (`Dashboard`, `Calendar`, `Progress`, `Projects`, `Activities`, `More`)
- Faol tab ostida **yashil chiziq (underline)** orqali ajratiladi
- O'ng tomonda (odatda): profil, bildirishnomalar

```
[LOGO]   Dashboard  Calendar  Progress  Projects  Activities  More
          ▔▔▔▔▔▔▔▔▔ (yashil underline — faol holat)
```

### 4.2 Qidiruv (Search bar)
- To'liq kenglikdagi, pastki burchaklari yumaloq (radius ~12px) input
- Fon: `--input-bg`, ichida kulrang lupa (search) ikonkasi va placeholder matni
- Border yo'q yoki juda nozik

### 4.3 Profil / Progress vidjeti
- Doira shaklidagi avatar (rasm)
- Avatar yonida foydalanuvchi nikneymi — **binafsha rangda, bold**
- Pastida: joriy dastur/kurs nomi (kulrang, kichik matn)
- Chap tomonda **level progress bar**: gorizontal yo'lak (track) qorong'i fonda, ustida teal-gradient to'ldirilgan qism, yonida "lvl 10: 33%" matni (yashil rangda foiz)

### 4.4 Statistika qatori (Stats row)
Dashboard pastki qismida gorizontal ajratilgan blok, har biri icon + qiymat + label ko'rinishida:
```
[icon] Jamoat nomi ↑159   |   Holat: 2 days   |   291¢ Coins   |   10 Peer Review points   |   5 Code Review points
```
- Raqamlar/qiymatlar **bold va oq**
- Label'lar kichik va kulrang
- Ba'zi qiymatlar (masalan "2 days") aksent rangda (ko'k/binafsha) ajratib ko'rsatiladi — muhimlikni bildirish uchun

### 4.5 Dekorativ fon shakllari
- Sahifaning yuqori chap va o'ng burchaklarida **abstrakt, "oqib turgan" blob/zigzag shakllar** — gradient (ko'k → yashil → teal) rangda
- Bu shakllar yumaloq burchakli kvadratchalardan tashkil topgan, bir-biriga ulangan "tasma" ko'rinishida
- Faqat dekorativ, funksional emas — sahifaning yuqori qismiga "hayot" qo'shadi

### 4.6 Kalendar (Calendar) sahifasi
- Fonida nozik grid (jadval) chiziqlari — soat bo'yicha qatorlar
- Har bir tadbir (event) — **to'liq rangli (ko'k) pill/karta**, ichida soat va tadbir nomi (bold)
- Bir-biriga yaqin tadbirlar bevosita ustma-ust/qator bo'lib joylashadi

### 4.7 Modal oyna (Popup)
- Qorong'i fon (`--bg-surface`), katta radius (~20px)
- Yuqorida: katta bold sarlavha + o'ng burchakda **X (yopish)** ikonkasi
- Pastda: label–value juftliklari (label kulrang, value oq yoki ko'k-havola)
- Eng pastda: **to'liq kenglikdagi yashil CTA tugma**, radius ~12px, qora matn

```css
.modal {
  background: var(--bg-surface);
  border-radius: 20px;
  padding: 32px;
}
.modal-title { font-size: 28px; font-weight: 700; }
.btn-primary {
  background: var(--accent-green);
  color: #0A0A0A;
  border-radius: 12px;
  padding: 14px 24px;
  width: 100%;
  font-weight: 600;
}
```

---

## 5. Komponent uslublari (umumlashtirilgan)

| Komponent | Border-radius | Fon | Izoh |
|---|---|---|---|
| Tugma (asosiy) | 12px | `--accent-green` | Qora matn, bold |
| Tugma (ikkilamchi/link) | — | shaffof | Ko'k matn |
| Karta (card) | 16–20px | `--bg-surface` | Yengil soya (shadow) yoki border |
| Input/Search | 12px | `--input-bg` | Border yo'q |
| Progress bar | 6–8px (pill) | track: qorong'i, fill: teal gradient | |
| Badge/Stat icon | — | rangli icon + matn | Coin, point belgilari uchun maxsus iconka |
| Modal | 20px | `--bg-surface` | Markazda, overlay fon bilan |

---

## 6. Gamifikatsiya elementlari (muhim dizayn xususiyati)

Bu platformaning eng o'ziga xos jihati — **o'quv jarayonini o'yin elementlari bilan boyitish**:
- **Level va progress bar** — foydalanuvchi qancha "level"da ekanini va foizini ko'rsatadi
- **Coin tizimi** — virtual valyuta (masalan "291¢")
- **Ball tizimi** — Peer Review va Code Review ballari alohida ko'rsatiladi
- **Tribe/jamoat** — foydalanuvchi a'zo bo'lgan jamoa va uning reytingi

O'z platformangizni qurayotganda, shu elementlarni saqlab qolish foydaliroq bo'ladi: foydalanuvchi profili yonida doim **progress, ball va valyuta** ko'rinib turishi kerak — bu motivatsiyani oshiradi.

---

## 7. Tavsiyalar — keyingi qadam

1. **DevTools orqali tekshiring:** platformaga kirib, istalgan elementni o'ng tugma bilan bosib "Inspect" qiling — aniq HEX rang kodlari, shrift nomi va o'lchamlarini ko'rasiz (Computed tab).
2. **Skrinshotlarni menga yuboring:** agar boshqa sahifalar (Profile, Projects, Activities) dizaynini ham tahlil qildirmoqchi bo'lsangiz — skrinshot tashlang, men har biri uchun shu formatda batafsil tahlil qilib beraman.
3. **Figma'ga ko'chiring:** shu rang/shrift tizimini Figma'da "Design Tokens" sifatida saqlab, undan keyin komponentlar (button, card, input) yaratishni boshlang.
4. **Frontend kodga o'tkazish:** Tailwind CSS ishlatsangiz, shu ranglarni `tailwind.config.js` dagi `theme.extend.colors` ichiga qo'shib qo'yishingiz mumkin — men buni ham tayyorlab bera olaman, agar kerak bo'lsa.

---

## 8. Xavfsizlik bo'yicha eslatma

Suhbat boshida platformaning haqiqiy parolingizni ulashgan edingiz — bu xavfsiz emas, chunki suhbat tarixi saqlanib qolishi mumkin. Tavsiya: **shu parolni imkon qadar tezroq almashtiring.**