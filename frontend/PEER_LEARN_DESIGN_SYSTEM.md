# Peer Learn — Design System & UI Spec (for AI Frontend Generation)

> **Qanday ishlatish:** Bu faylni `BACKEND_API.md` bilan **birga** Google AI Studio (Gemini) yoki Claude (Sonnet/Opus)ga bering va shunday so'rang: *"Quyidagi BACKEND_API.md kontraktiga va PEER_LEARN_DESIGN_SYSTEM.md dizaynitga to'liq mos React + TypeScript + Tailwind frontend yarat."* Bu hujjat — 21-School platformasining (`platform.21-school.ru`) haqiqiy skrinshotlaridan **piksel darajasida o'lchab olingan** rang tizimi asosida qurilgan, lekin **Peer Learn**ning o'z data modeliga (slot, peer point, peer coin, XP, review) moslab qayta ishlangan.

---

## 0. Dizayn falsafasi

Peer Learn — **dark-mode-first**, gamifikatsiyalashgan, talaba-talabaga (peer-to-peer) o'qitish platformasi. Vizual til:

- Chuqur ko'k-qora fon (deep navy) — ko'zni charchatmaydi, kechqurun ham kun bo'yi ishlatiladi
- Karta-asoslangan (card-based) layout — har bir slot, har bir statistika alohida "karta"
- **Pill/badge** elementlar — status, ball, daraja ko'rsatish uchun (dumaloq, rangli yorliqlar)
- Yumshoq gradient progress barlar — XP/level ko'rsatish uchun
- Minimal, geometrik dekorativ shakllar — sahifa "jonli" ko'rinishi uchun, lekin funksiyaga xalaqit bermaydi
- Til: **faqat o'zbek tilida** (barcha matn, tugma, xabarlar)

---

## 1. Rang tizimi (skrinshotlardan piksel darajasida olingan)

```css
:root {
  /* ===== Fon (Background) ===== */
  --bg-primary: #1D2633;      /* Asosiy sahifa foni — eng ko'p ishlatiladigan rang */
  --bg-surface: #2C384A;      /* Kartalar, modal, pill fonlar */
  --bg-surface-alt: #263040;  /* Ikkilamchi panel, input fon, hover holat */
  --bg-elevated: #324151;     /* Hover/active holatdagi elementlar, border */

  /* ===== Brend ranglari ===== */
  --brand-teal: #18D6C7;      /* Logotip, asosiy brend rangi, grafik chiziqlari */
  --brand-mint: #44EB99;      /* Faol nav tab, asosiy CTA tugma, progress bar fill */

  /* ===== Status/Aksent ranglar ===== */
  --accent-blue: #008BFF;     /* Info, "ochiq" status, havolalar, CRP ball */
  --accent-purple: #861BE3;   /* "Davom etmoqda" status, tag-badge */
  --accent-purple-soft: #A24FEA; /* Coin pill, ikkilamchi binafsha */
  --accent-amber: #F1A700;    /* Peer Review ball, ogohlantirish badge */
  --accent-red: #FF5C5C;      /* YANGI — xato, bekor qilish, "absent" statusi uchun (asl platformada yo'q, lekin zarur) */

  /* ===== Neytral ranglar ===== */
  --neutral-pill: #DDE3E9;    /* Och kulrang pill (masalan XP ball, progress track) */
  --text-primary: #FFFFFF;
  --text-secondary: #C6CFDA;
  --text-muted: #8B95A5;
  --border-color: #324151;
}
```

### Tailwind config (tayyor, nusxa ko'chiring)

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        bg: {
          primary: '#1D2633',
          surface: '#2C384A',
          surfaceAlt: '#263040',
          elevated: '#324151',
        },
        brand: {
          teal: '#18D6C7',
          mint: '#44EB99',
        },
        accent: {
          blue: '#008BFF',
          purple: '#861BE3',
          purpleSoft: '#A24FEA',
          amber: '#F1A700',
          red: '#FF5C5C',
        },
        neutral: {
          pill: '#DDE3E9',
        },
        text: {
          primary: '#FFFFFF',
          secondary: '#C6CFDA',
          muted: '#8B95A5',
        },
      },
      borderRadius: {
        card: '20px',
        pill: '999px',
        input: '12px',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
}
```

---

## 2. Tipografiya

- **Shrift:** `Inter` (Google Fonts) — barcha matn uchun
- **H1 (sahifa sarlavhasi):** 28–32px, weight 700
- **H2 (karta sarlavhasi):** 18–20px, weight 600
- **Body:** 14–16px, weight 400, `--text-primary` yoki `--text-secondary`
- **Label/kichik matn:** 12–13px, weight 400, `--text-muted`
- **Raqam/statistika (stat value):** 18–22px, weight 700, `--text-primary`

---

## 3. Asosiy komponentlar (reusable)

### 3.1 Tugmalar
| Variant | Fon | Matn | Qachon ishlatiladi |
|---|---|---|---|
| Primary | `--brand-mint` (#44EB99) | qora (#0A0E14) | Asosiy harakat: "Bron qilish", "Saqlash", "Boshlash" |
| Secondary | shaffof, border `--border-color` | oq | Ikkilamchi harakat: "Bekor qilish" |
| Danger | `--accent-red` | oq | "Yo'qligini belgilash", o'chirish |
| Link | shaffof | `--accent-blue` | "Barchasini ko'rish", navigatsiya havolalar |

Barchasi: `border-radius: 12px`, `padding: 12px 20px`, `font-weight: 600`.

### 3.2 Status/Pill badge (Slot status uchun — backend enum'ga mos)
| Slot status (backend) | Pill matni (UZ) | Fon rangi |
|---|---|---|
| `open` | Ochiq | `--accent-blue` |
| `booked` | Bron qilingan | `--accent-purple` |
| `in_progress` | Davom etmoqda | `--brand-mint` (qora matn bilan, "live" hissi uchun) |
| `completed` | Yakunlandi | `--brand-teal` |
| `cancelled` | Bekor qilingan | `--bg-elevated` (kulrang, neytral) |
| `absent` | Kelmadi | `--accent-red` |

Ball/coin pill'lar (Profile va Dashboard uchun):
| Pill | Fon | Matn rangi |
|---|---|---|
| XP | `--neutral-pill` (#DDE3E9) | qora |
| Peer Points (PRP) | `--accent-amber` | qora |
| Peer Coins | `--accent-purple-soft` | oq |

### 3.3 Karta (Card)
```css
.card {
  background: var(--bg-surface);
  border-radius: 20px;
  padding: 24px;
  border: 1px solid var(--border-color);
}
```

### 3.4 Progress bar (Level/XP)
```css
.progress-track {
  height: 8px;
  border-radius: 999px;
  background: var(--neutral-pill);
}
.progress-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--brand-teal), var(--brand-mint));
}
```
Yonida matn: `lvl {level}: {xp_to_next_level}%` — yashil (`--brand-mint`) rangda.

### 3.5 Input / Qidiruv
```css
.input, .search-bar {
  background: var(--bg-surface-alt);
  border: none;
  border-radius: 12px;
  padding: 12px 16px;
  color: var(--text-primary);
}
.input::placeholder { color: var(--text-muted); }
```

### 3.6 Modal
```css
.modal {
  background: var(--bg-surface);
  border-radius: 20px;
  padding: 32px;
  max-width: 480px;
}
```
Yuqorida: sarlavha (bold, 24–28px) + o'ng burchakda `X` yopish ikonkasi. Pastda: to'liq kenglikdagi primary tugma.

### 3.7 Top Navigation (Desktop)
```
[LOGO]   Bosh sahifa   Slotlar   Qidiruv   Reyting   Profil        [🔔] [👤▾]
          ▔▔▔▔▔▔▔▔▔▔ (faol tabning ostida --brand-mint chiziq, 2px)
```
- Fon: `--bg-primary` (sahifa foni bilan bir xil, chegarasiz, faqat pastida nozik `--border-color` chiziq)
- Faol tab: oq matn + ostida mint-yashil underline
- Nofaol tab: `--text-secondary`

### 3.8 Bottom tab bar (Mobile)
5 ta ikonka: Bosh sahifa, Slotlar, Qidiruv (markazda, doira ichida, ko'tarilgan), Reyting, Profil. Faol ikonka — `--brand-mint` rangda, qolganlari `--text-muted`.

### 3.9 Avatar
Doira (`border-radius: 50%`), agar `avatar_url` bo'lmasa — bosh harf bilan placeholder, fon `--bg-elevated`.

---

## 4. Sahifalar — API'ga to'liq moslangan spec

### 4.1 `/login` — Kirish sahifasi

**Layout:** Markazda kichik karta (max-width 400px), fonida xira dekorativ blob shakllar (burchaklarda, `--brand-teal` → `--brand-mint` gradient).

- Logotip (yuqorida, markazda)
- Sarlavha: "Tizimga kirish"
- Input: "School21 login"
- Input: "Parol" (password type)
- Primary tugma: "Kirish" → `POST /auth/login`

**Ikkita holat (backend javobiga qarab):**
1. `status: "ok"` → token saqlanadi → `onboarding_done` false bo'lsa `/onboarding`ga, aks holda `/dashboard`ga yo'naltirish
2. `status: "need_telegram"` → yangi ekran: "Telegram orqali tasdiqlang" + `bot_url` ga link tugma ("Telegram botni ochish", `--brand-mint` tugma) + 6-xonali OTP kod input + "Tasdiqlash" tugma → `POST /auth/verify-code`

Xato holat: input ostida qizil (`--accent-red`) matn bilan `detail` xabari ko'rsatiladi.

### 4.2 `/onboarding` — 2 bosqichli forma

**Bosqich 1 — Track tanlash:**
- Sarlavha: "Yo'nalishingizni tasdiqlang"
- `GET /onboarding/track` dan kelgan `core_program` ko'rsatiladi (read-only matn)
- 6 ta katta tanlash kartasi (grid, 3x2): Web, Mobile, GameDev, DataScience, DevOps, Blockchain — har biri icon + nom, tanlanganda `--brand-mint` border bilan ajraladi
- "Davom etish" tugma → `POST /onboarding/confirm`

**Bosqich 2 — Tillar:**
- Sarlavha: "Qaysi tillarda gaplasha olasiz?"
- Pill-style multi-select chiplar: O'zbek, Русский, English, va h.k. — tanlanganlar `--brand-mint` fon bilan
- "Yakunlash" tugma → `POST /onboarding/languages` → muvaffaqiyatli bo'lsa `/dashboard`ga

Progress indikator yuqorida: 2 ta nuqta, joriy bosqich `--brand-mint` rangda.

### 4.3 `/dashboard` — Bosh sahifa (asl Dashboard skrinshotiga eng yaqin sahifa)

**Yuqori blok** (asl platformadagi struktura bilan bir xil):
```
[LOGO]        Bosh sahifa  Slotlar  Qidiruv  Reyting             [🔔] [👤]

  lvl {level}: {xp_to_next_level}%      ( avatar )   {first_name} {last_name}
  ▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░                            {core_program} · {main_track}
```

**Statistika qatori** (`user` obyektidan, gorizontal, 5 ustun — asl "Wolverine 159 / 2 days / 401¢" qatoriga mos):
```
[🛡] {coalition_name}     {current_location}      {xp} XP        {peer_points}        {peer_coins}
     Jamoa                  Joriy joylashuv         Tajriba       Peer ball              Coinlar
```

**Ikki ustunli karta blok** (`active_slots` asosida, asl "Events / Your agenda" ga mos):

*Chap karta — "Faol slotlar"* (sarlavha o'ng tomonida "Barchasi" linki → `/slots`):
- Har bir `active_slots[]` elementi — kichik qator: status pill (§3.2) + `reviewer_project`/`reviewee_project` + vaqt (`start_time`) + "Batafsil" tugma
- Bo'sh bo'lsa: "Hozircha faol slotlar yo'q" + "Slot yaratish yoki qidirish" tugma

*O'ng karta — "Bildirishnomalar"* (sarlavha o'ng tomonida "Barchasi" linki → `/notifications`):
- So'nggi 3–4 ta `notification`, o'qilmaganlari nuqta-indikator bilan (`--brand-mint` doira)
- Bo'sh bo'lsa: "Sizda yangi bildirishnomalar yo'q"

Fon dekoratsiya: sahifa yuqori chap/o'ng burchaklarida xira, kichik gradient blob shakllari (asl dizayndagi kabi, lekin opacity 15–20% — diqqatni asosiy kontentdan chalg'itmasligi uchun).

### 4.4 `/slots` — Slotlar ro'yxati + Kalendar ko'rinish

Ikki tab: **"Ro'yxat"** va **"Kalendar"** (asl Calendar sahifasiga mos).

**Kalendar tab:** Haftalik grid (7 kun ustunlar, soatlar qatorlar — asl skrinshotdagi aynan shu struktura). Har bir slot — rangli pill-karta (status bo'yicha §3.2 rangda), bosilganda popup ochiladi (asl "Peer Review slot" / "Create slot" modaliga mos):

```
┌─────────────────────────┐
│ Slot yaratish        ✕  │
│                          │
│ Loyiha:  [dropdown ▾]    │  ← /slots/my/teachable-projects dan
│ Sana:    [date picker]   │
│ Vaqt:    [from] — [to]   │
│ ☐ Online / ☐ Offline     │
│                          │
│  [    Saqlash    ]       │  ← POST /slots/
└─────────────────────────┘
```

> **Biznes qoida UI'da:** agar campus = "tashkent" bo'lsa, "Offline" checkbox disabled bo'lib, ostida kichik matn: "Toshkent kampusi uchun faqat online slotlar mavjud" (`--text-muted`).

**Ro'yxat tab:** Filter chiplar yuqorida (`Barchasi / Ochiq / Bron qilingan / Yakunlangan`), pastda vertikal karta ro'yxati. Har bir karta: status pill, loyiha nomi, vaqt, kampus ikonkasi (online bo'lsa 💻, offline bo'lsa 📍).

### 4.5 `/slots/:id` — Slot tafsiloti

Karta ko'rinishida:
- Status pill (katta)
- `reviewer_project` / `reviewee_project`
- Vaqt: `start_time` – `end_time`, agar `actual_start` bor bo'lsa — "Boshlangan: {actual_start}"
- Kampus + online/offline

**Harakat tugmalari — `slot.reviewer_id`/`reviewee_id` ni joriy userning `id`si bilan solishtirib, mos tugmalar ko'rsatiladi:**

| Holat | Kim ko'radi | Tugma | Endpoint |
|---|---|---|---|
| `status=open`, men reviewer emasman | har kim | "Bron qilish" (primary) | `POST /slots/{id}/book` |
| `status=open`, men reviewerman | reviewer | "Bekor qilish" (secondary) | `DELETE /slots/{id}` |
| `status=booked` | ikkalasi | "Boshlash" (primary, faollashadi) | `POST /slots/{id}/start` |
| `status=booked`, men reviewerman | reviewer | + "Bekor qilish" (danger) | `DELETE /slots/{id}` |
| `status=in_progress`, 15 daqiqa o'tmagan | ikkalasi | "Yakunlash" tugmasi **disabled**, ostida countdown: "Yakunlash uchun {N} daqiqa qoldi" | — |
| `status=in_progress`, 15 daqiqa o'tgan | ikkalasi | "Yakunlash" (primary, faol) | `POST /slots/{id}/finish` |
| `status=booked`/`in_progress` | ikkalasi | "Kelmadi deb belgilash" (kichik, danger, pastda) | `POST /slots/{id}/absent` |
| `status=completed`, hali review qoldirilmagan | ikkalasi | "Baholash" → `/review?slot={id}` | — |

WebSocket holatlari (`slot.both_started`, `slot.both_finished`) kelganda — sahifa real-vaqtda yangilanadi, kichik toast bildirishnoma chiqadi ("Ikkalangiz ham boshladingiz!").

### 4.6 `/search` — Loyiha bo'yicha qidiruv

- Katta search input (§3.5): "Loyiha nomini kiriting..." → `GET /slots/search?project=`
- Tezkor chiplar: `GET /slots/my/in-progress-projects` dan — foydalanuvchi hozir o'tayotgan loyihalar (bosilsa avtomatik shu loyiha bo'yicha qidiradi)
- Natijalar — `SlotSearchResult[]` kartalari: vaqt, kampus, online/offline belgisi, "Bron qilish" tugmasi

### 4.7 `/leaderboard` — Reyting

3 ta tab (pill-toggle): **"Eng ko'p XP"**, **"Eng ko'p o'rgatgan"**, **"Eng ko'p o'rgangan"** → mos `most-xp` / `most-taught` / `most-learned` endpointlari.

Ro'yxat: har bir qator — `rank` (katta raqam yoki 🥇🥈🥉 birinchi 3 ta uchun), ism-familiya, `value`. Joriy foydalanuvchi qatori `--brand-mint` chap-border bilan ajratiladi.

Yuqorida oy tanlash dropdown (ixtiyoriy, `leaderboard/history` uchun).

### 4.8 `/profile` (o'zim) va `/profile/:username` (boshqalar) — asl "My-profile" sahifasiga eng yaqin

**Chap karta** (asl skrinshotdagi struktura bilan bir xil):
- Avatar (katta, doira)
- Ism-familiya (bold)
- `core_program` · `main_track`
- Level progress bar (§3.4)
- Points pill qatori: XP, PRP (Peer Points), Coins (§3.2 jadvali)
- "Peer feedback" bo'limi — agar backend kelajakda shu turdagi reyting qaytarsa; hozircha **stats** obyektidan: `positive_reviews`, `negative_reviews`, `all_reviews`, `taught_count`, `learned_count` — har biri label + qiymat qatori
- Email, kampus/joylashuv
- (faqat o'z profilida) "Parolni o'zgartirish", "Telegramni uzish" tugmalari → tegishli sahifa/modal

**O'ng katta karta — "XP grafigi":**
- `GET /profile/skills` dan kelgan ma'lumot asosida **chiziqli grafik (line chart)**, X-o'qda vaqt, Y-o'qda XP — `--brand-teal` rangli chiziq, ostida engil gradient fill (`--brand-teal` 10% opacity)
- Skills radar/spider chart (agar skills endpoint shunday struktura qaytarsa) — `--brand-mint` chiziq

**Boshqa userning profilida** (`UserPublic` — points/email yo'q): faqat ism, daraja, XP, kampus, track, koalitsiya ko'rsatiladi + "Reyting" tugmasi (agar slot ochiq bo'lsa "Slotini ko'rish").

**Tabs (o'z profilida, asl dizayndagi kabi):** `Ma'lumot` | `Bildirishnomalar` | `Parolni o'zgartirish` | `Hamyon (Wallet)`

### 4.9 `/review?slot=:id` — Baholash sahifasi

Markazda kichik karta:
- Slot ma'lumoti (loyiha, hamkor ismi) qisqacha yuqorida
- Katta ikkita tugma: 👍 "Ijobiy" (`--brand-mint`) / 👎 "Salbiy" (`--accent-red`) — bittasi tanlanadi
- Izoh maydoni (textarea, max 500 belgi, pastda hisoblagich "320/500")
- "Yuborish" tugma → `POST /reviews/`

### 4.10 `/notifications` — Bildirishnomalar

Vertikal ro'yxat, har bir element:
- Chap tomonda turga mos icon (§5 jadvaliga qarang)
- `title` (bold), `body` (`--text-secondary`)
- O'qilmagan bo'lsa — chap chetida `--brand-mint` vertikal chiziq + fon biroz yorqinroq (`--bg-surface-alt`)
- O'ng tomonda vaqt (`created_at`, nisbiy: "5 daqiqa oldin")

Yuqorida: "Barchasini o'qilgan deb belgilash" link tugma → `POST /notifications/read-all`

### 4.11 `/settings` — Sozlamalar

Oddiy forma karta ichida:
- Til tanlash (dropdown) → `PATCH /settings/language`
- Tema: Light / Dark / System (toggle, 3 tugma) → `PATCH /settings/theme` (mahalliy ham saqlanadi)
- Kampus (read-only, School21'dan keladi)

### 4.12 `/admin/*` — faqat `is_admin: true` bo'lsa ko'rinadi

Yon menyuda alohida "Admin" bo'limi (`--accent-red` belgisi bilan ajratiladi, ehtiyot chorasi sifatida). Ichida: Foydalanuvchilar jadvali (qidiruv, blok/o'chirish tugmalari), Slotlar monitoringi, Statistika kartalari (`total_users`, `total_slots`, `completed_slots`, `avg_duration_minutes` — 4 ta katta raqam karta, dashboard stat-row uslubida).

---

## 5. Bildirishnoma turlari → Ikonka xaritasi

| `type` | Ikonka (lucide-react) | Rang |
|---|---|---|
| `slot_booked` | `calendar-check` | `--accent-blue` |
| `slot_started` | `play-circle` | `--brand-mint` |
| `slot_completed` | `check-circle-2` | `--brand-teal` |
| `slot_cancelled` | `x-circle` | `--accent-red` |
| `review_received` | `star` | `--accent-amber` |
| `absent_given` / `absent_received` | `user-x` | `--accent-red` |
| `system` | `bell` | `--text-muted` |

---

## 6. Layout qoidalari

- **Desktop (≥1024px):** Yuqori gorizontal nav (§3.7), kontent markazlashtirilgan, max-width 1280px
- **Mobile (<1024px):** Yuqorida faqat logo + bildirishnoma + profil ikonkasi; pastda bottom tab bar (§3.8)
- **Dark mode — default va asosiy.** Light mode ixtiyoriy (`/settings` orqali), agar qo'shilsa — fon ranglar oqartiriladi, lekin brend ranglar (`--brand-teal`, `--brand-mint`) saqlanadi
- Barcha sana/vaqt: `toLocaleString('uz-UZ', ...)`

---

## 7. Mikro-matn lug'ati (UZ) — tezkor murojaat

| Inglizcha tushuncha | UZ matn |
|---|---|
| Login | Kirish |
| Logout | Chiqish |
| Book slot | Bron qilish |
| Cancel | Bekor qilish |
| Start | Boshlash |
| Finish | Yakunlash |
| Mark absent | Kelmadi deb belgilash |
| Search | Qidirish |
| Leaderboard | Reyting |
| Profile | Profil |
| Notifications | Bildirishnomalar |
| Settings | Sozlamalar |
| Save | Saqlash |
| Submit review | Baholashni yuborish |
| Positive / Negative | Ijobiy / Salbiy |
| No data | Ma'lumot yo'q |
| Loading... | Yuklanmoqda... |

---

## 8. AI kod generatoriga qo'shimcha ko'rsatma

Agar shu hujjat Google AI Studio / Claude'ga `BACKEND_API.md` bilan birga berilsa, quyidagilarni alohida ta'kidlang:

1. Barcha rang **CSS custom property** (`var(--bg-primary)` va h.k.) yoki Tailwind custom class orqali ishlatilsin — hardcoded HEX kod yozilmasin.
2. Har bir sahifa komponenti tegishli `BACKEND_API.md` endpointiga **aniq** ulansin (TanStack Query bilan, §11-bo'limdagi arxitekturaga mos).
3. Slot status va notification type'lar uchun **markazlashtirilgan** mapping fayli yarating (`src/constants/statusMap.ts`) — §3.2 va §5 jadvallaridagi qiymatlar bilan, hardcode qilib har joyda takrorlamang.
4. Barcha matn — **faqat o'zbek tilida** (§7 lug'atidan foydalaning, kerak bo'lsa kengaytiring).
