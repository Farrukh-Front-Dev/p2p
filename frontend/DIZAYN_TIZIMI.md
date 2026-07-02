# Dizayn Tizimi — To'liq Qo'llanma (3D Neo-Brutalist)

> Bu hujjat CareerHub21 loyihasidan ajratib olingan **dizayn tizimi**ni boshqa platformaga ko'chirish va moslashtirish uchun yozilgan. Bu yerda dizayn falsafasi, ranglar, shriftlar, komponentlar va tayyor kod namunalari bor. Boshqa loyihada xohlagancha o'zgartirib foydalanishingiz mumkin.

---

## 📑 Mundarija

1. [Dizayn falsafasi](#1-dizayn-falsafasi)
2. [Texnologiyalar steki](#2-texnologiyalar-steki)
3. [Ranglar tizimi](#3-ranglar-tizimi)
4. [Shriftlar (Typography)](#4-shriftlar-typography)
5. [3D soya tizimi](#5-3d-soya-tizimi)
6. [Dark Mode (3 darajali fon)](#6-dark-mode-3-darajali-fon)
7. [Asosiy komponentlar](#7-asosiy-komponentlar)
8. [Loading va Skeleton](#8-loading-va-skeleton)
9. [Animatsion fon (Squares)](#9-animatsion-fon-squares)
10. [Responsive dizayn](#10-responsive-dizayn)
11. [Eng yaxshi amaliyotlar](#11-eng-yaxshi-amaliyotlar)
12. [Boshqa platformaga ko'chirish bo'yicha qadamlar](#12-boshqa-platformaga-kochirish)

---

## 1. Dizayn falsafasi

Bu dizayn **dadil, o'ynoqi va zamonaviy** ko'rinishni yaratadi. Asosiy g'oyalar:

- **3D soyalar** — chuqurlik va "ushlab bo'ladigan" his beradi (`box-shadow` siljishsiz, qattiq qora)
- **Qalin chegaralar** — `border-2 border-gray-900` (har doim 2px qora)
- **Yumaloq burchaklar** — do'stona ko'rinish uchun (`rounded-xl`, `rounded-2xl`, `rounded-3xl`)
- **Yorqin gradientlar** — energiya va e'tibor uchun (cyan → green)
- **Hover animatsiyalari** — interaktivlik uchun (bosilganda pastga "cho'kadi")

Bu uslub **Neo-Brutalism** deb ataladi: qattiq soyalar, kontrast chegaralar va o'ynoqi ranglar.

---

## 2. Texnologiyalar steki

Asl loyiha quyidagilarda qurilgan:

| Texnologiya | Versiya | Vazifasi |
|---|---|---|
| Next.js | ^16 | React framework (App Router) |
| React | 19 | UI kutubxonasi |
| Tailwind CSS | v4 | Stillar (CSS-first konfiguratsiya) |
| TypeScript | ^5 | Tiplar |
| lucide-react | ^0.575 | Ikonlar |
| Redux Toolkit | ^2 | State boshqaruvi |
| react-i18next | — | Tarjima (uz/ru/en) |
| recharts | ^3 | Grafiklar |

> **Eslatma:** Dizaynni boshqa stekda ham (oddiy HTML+CSS, Vue, Svelte) ishlatish mumkin. Tailwind v4 ishlatilgani uchun ranglar `globals.css` ichida `@theme` orqali aniqlangan, alohida `tailwind.config.js` shart emas.

---

## 3. Ranglar tizimi

### Brend ranglar
```css
--color-brand-cyan:  #38C9E6;   /* asosiy ko'k */
--color-brand-green: #43E8A0;   /* asosiy yashil */
```

Asosiy gradient hamma joyda ishlatiladi:
```css
linear-gradient(135deg, #38C9E6 0%, #43E8A0 100%)
```
Tailwind'da: `bg-linear-to-br from-[#38C9E6] to-[#43E8A0]`

### Primary palette (cyan asosidagi)
```css
--color-primary-50:  #E6F9FD;
--color-primary-100: #CCF3FB;
--color-primary-200: #99E7F7;
--color-primary-300: #66DBF3;
--color-primary-400: #38C9E6;   /* asosiy */
--color-primary-500: #2BA8C4;
--color-primary-600: #2287A2;
--color-primary-700: #1A6680;
--color-primary-800: #11455E;
--color-primary-900: #09243C;
```

### Secondary palette (green asosidagi)
```css
--color-secondary-50:  #E8FCF3;
--color-secondary-100: #D1F9E7;
--color-secondary-200: #A3F3CF;
--color-secondary-300: #75EDB7;
--color-secondary-400: #43E8A0;   /* asosiy */
--color-secondary-500: #36BA80;
--color-secondary-600: #2A8C60;
--color-secondary-700: #1D5E40;
--color-secondary-800: #113020;
--color-secondary-900: #081810;
```

### Aksent va holat ranglari
```css
--pink:        #FF9B9B;   /* ikkilamchi tugma */
--pink-hover:  #FF8888;
--border:      #000000;   /* gray-900, chegara */
```

Holat ranglari (Tailwind klasslari):
- **Success:** `bg-green-100 text-green-700` (dark: `bg-green-900/20 text-green-400`)
- **Warning:** `bg-yellow-100 text-yellow-700` (dark: `bg-yellow-900/20 text-yellow-400`)
- **Error:** `bg-red-100 text-red-700` (dark: `bg-red-900/20 text-red-400`)
- **Info:** `bg-blue-100 text-blue-700` (dark: `bg-blue-900/20 text-blue-400`)

### Ikon gradient variantlari
```css
cyan-blue:      from-cyan-400 to-blue-500
pink-red:       from-pink-400 to-red-500
purple-indigo:  from-purple-400 to-indigo-500
green-emerald:  from-green-400 to-emerald-500
```

> **O'zgartirish maslahati:** Boshqa platforma uchun faqat `--color-brand-cyan` va `--color-brand-green` ni o'zgartirsangiz, butun tizim yangi rangga moslashadi. Masalan binafsha brend uchun: `#8B5CF6` → `#EC4899`.

---

## 4. Shriftlar (Typography)

Ikki shrift kombinatsiyasi ishlatiladi:

| Shrift | Qayerda | Manba |
|---|---|---|
| **Montserrat** | Sarlavhalar (h1–h6), tugmalar, label | Google Fonts |
| **IBM Plex Mono** | Asosiy matn (body) | Google Fonts |

Next.js'da ulanishi:
```tsx
import { Montserrat, IBM_Plex_Mono } from "next/font/google";

const montserrat = Montserrat({
  variable: "--font-montserrat",
  subsets: ["latin"],
  weight: ["400", "600", "700", "800"],
  display: "swap",
});

const ibmPlexMono = IBM_Plex_Mono({
  variable: "--font-ibm-plex-mono",
  subsets: ["latin"],
  weight: ["400", "600"],
  display: "swap",
});
```

CSS qoidalari (`globals.css`):
```css
body { font-family: var(--font-ibm-plex-mono); }
h1, h2, h3, h4, h5, h6 { font-family: var(--font-montserrat); }
button, a[class*="btn"] { font-family: var(--font-montserrat); }
label { font-family: var(--font-montserrat); }
```

Utility klasslar: `.font-montserrat`, `.font-ibm-plex-mono`, `.text-heading`, `.text-body`.

---

## 5. 3D soya tizimi

Bu — dizaynning yuragi. Soyalar **qattiq** (blur yo'q), qora va siljimaydigan.

### Soya o'lchamlari
```css
shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]   /* kichik */
shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]   /* o'rta */
shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]   /* katta (default card) */
shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]   /* juda katta (modal) */
```

### Hover effektlari (2 xil)
```css
/* Card hover — pastga "cho'kadi" (soya kichrayadi + element siljiydi) */
hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px] transition-all

/* Button hover — yuqoriga "ko'tariladi" (soya kattalashadi) */
hover:shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] hover:-translate-x-[2px] hover:-translate-y-[2px] transition-all
```

### Tayyor CSS klasslar (`globals.css`'ga qo'shing)
```css
/* Asosiy 3D soya */
.shadow-3d {
  border: 2px solid rgba(0, 0, 0, 1);
  box-shadow: 4px 4px 0px 0px rgba(0, 0, 0, 1);
  transition: all 0.2s ease;
}
.shadow-3d:hover {
  box-shadow: 2px 2px 0px 0px rgba(0, 0, 0, 1);
  transform: translate(2px, 2px);
}

/* Card — hover bilan siljiydi */
.card-3d {
  border: 2px solid rgba(0, 0, 0, 1);
  box-shadow: 4px 4px 0px 0px rgba(0, 0, 0, 1);
  transition: all 0.2s ease;
}
.card-3d:hover {
  box-shadow: 2px 2px 0px 0px rgba(0, 0, 0, 1);
  transform: translate(2px, 2px);
}

/* Static card — Navbar/dropdown uchun (siljimaydi, faqat soya o'zgaradi) */
.card-3d-static {
  border: 2px solid rgba(0, 0, 0, 1);
  box-shadow: 4px 4px 0px 0px rgba(0, 0, 0, 1);
  transition: box-shadow 0.2s ease;
}
.card-3d-static:hover {
  box-shadow: 3px 3px 0px 0px rgba(0, 0, 0, 1);
}

/* Gradient tugma */
.btn-3d {
  background: linear-gradient(135deg, #38C9E6 0%, #43E8A0 100%);
  color: white;
  font-weight: 600;
  border: 2px solid rgba(0, 0, 0, 1);
  box-shadow: 4px 4px 0px 0px rgba(0, 0, 0, 1);
  transition: all 0.2s ease;
  cursor: pointer;
}
.btn-3d:hover:not(:disabled) {
  background: linear-gradient(135deg, #2BA8C4 0%, #36BA80 100%);
  box-shadow: 2px 2px 0px 0px rgba(0, 0, 0, 1);
  transform: translate(2px, 2px);
}
.btn-3d:disabled { opacity: 0.5; cursor: not-allowed; }
```

> ⚠️ **Muhim:** Navbar, dropdown, sticky/fixed elementlar uchun `card-3d-static` ishlating — `translate` ishlatilsa, gorizontal scroll muammosi chiqadi.

### Burchak radiuslari
```css
rounded-lg    /* 8px  — kichik badge */
rounded-xl    /* 12px — tugma, input */
rounded-2xl   /* 16px — o'rta card, ikon */
rounded-3xl   /* 24px — katta card */
```

---

## 6. Dark Mode (3 darajali fon)

Dark mode `class` strategiyasi bilan ishlaydi (`<html class="dark">`). Professional ko'rinish uchun **3 darajali fon ierarxiyasi** ishlatiladi:

```
1-daraja: Sahifa foni (eng quyuq)      → #1E2A38  (dark-page)
   └─ 2-daraja: Kontent konteyner       → #2A3442  (dark-bg)
        └─ 3-daraja: Ichki elementlar   → #34495E  (dark-surface)
```

### CSS o'zgaruvchilari
```css
--color-dark-page:    #1E2A38;   /* sahifa foni */
--color-dark-bg:      #2A3442;   /* kartalar, kontent */
--color-dark-surface: #34495E;   /* ichki kartalar */
--color-dark-input:   #1E2A38;   /* input maydonlari */
--color-dark-border:  #4A5F7F;   /* chegaralar */
--color-dark-text:    #FFFFFF;   /* asosiy matn */
--color-dark-text-secondary: #B0BEC5;  /* ikkilamchi matn */
```

### Foydalanish
```tsx
{/* 1-daraja — sahifa */}
<div className="min-h-screen bg-gray-50 dark:bg-dark-page">

  {/* 2-daraja — card */}
  <div className="bg-white dark:bg-dark-bg rounded-3xl p-8">

    {/* 3-daraja — ichki element */}
    <div className="bg-gray-50 dark:bg-dark-surface rounded-2xl p-6">
      ...
    </div>
  </div>
</div>
```

### Theme toggle (localStorage bilan)
```tsx
"use client";
import { useEffect } from "react";

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    const saved = localStorage.getItem("theme");
    if (saved === "dark") document.documentElement.classList.add("dark");
    else if (saved === "light") document.documentElement.classList.remove("dark");
    else if (window.matchMedia("(prefers-color-scheme: dark)").matches)
      document.documentElement.classList.add("dark");
  }, []);
  return <>{children}</>;
}
```

> **Tailwind v4 eslatma:** Dark variant `globals.css`'da quyidagicha aniqlangan:
> ```css
> @custom-variant dark (&:where(.dark, .dark *));
> ```

---

## 7. Asosiy komponentlar

### Card3D
```tsx
interface Card3DProps {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
  hover?: boolean;  // default: true
}

export default function Card3D({ children, className = "", onClick, hover = true }: Card3DProps) {
  const base = "bg-white dark:bg-dark-bg rounded-3xl border-2 border-gray-900 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-all";
  const hoverCls = hover ? "hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px]" : "";
  const clickCls = onClick ? "cursor-pointer" : "";
  return <div className={`${base} ${hoverCls} ${clickCls} ${className}`} onClick={onClick}>{children}</div>;
}
```

### Button3D
```tsx
interface Button3DProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: "gradient" | "white" | "outline";   // default: gradient
  fullWidth?: boolean;
}

export default function Button3D({ children, variant = "gradient", fullWidth = false, className = "", disabled, ...props }: Button3DProps) {
  const base = "font-semibold border-2 border-gray-900 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-all flex items-center justify-center gap-2";
  const hover = !disabled ? "hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px]" : "";
  const width = fullWidth ? "w-full" : "";
  const dis = disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer";
  const variants = {
    gradient: "bg-linear-to-br from-[#38C9E6] to-[#43E8A0] text-white",
    white: "bg-white dark:bg-dark-surface text-gray-900 dark:text-white",
    outline: "bg-transparent text-gray-900 dark:text-white",
  };
  return <button className={`${base} ${hover} ${width} ${dis} ${variants[variant]} ${className}`} disabled={disabled} {...props}>{children}</button>;
}
```

### Icon3D
```tsx
type GradientType = "cyan-blue" | "pink-red" | "purple-indigo" | "green-emerald";
type SizeType = "sm" | "md" | "lg";

const gradients = {
  "cyan-blue": "from-cyan-400 to-blue-500",
  "pink-red": "from-pink-400 to-red-500",
  "purple-indigo": "from-purple-400 to-indigo-500",
  "green-emerald": "from-green-400 to-emerald-500",
};
const sizes = { sm: "w-10 h-10", md: "w-12 h-12", lg: "w-14 h-14" };

export default function Icon3D({ children, gradient = "cyan-blue", size = "md", className = "" }: {
  children: ReactNode; gradient?: GradientType; size?: SizeType; className?: string;
}) {
  return (
    <div className={`${sizes[size]} rounded-2xl bg-linear-to-br ${gradients[gradient]} flex items-center justify-center border-2 border-gray-900 shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] ${className}`}>
      {children}
    </div>
  );
}
```

### Tugmalar (to'g'ridan-to'g'ri klass bilan)
```tsx
{/* Primary (gradient) */}
<button className="px-6 py-3 bg-linear-to-br from-[#38C9E6] to-[#43E8A0] text-white font-bold rounded-xl border-2 border-gray-900 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] hover:-translate-x-[2px] hover:-translate-y-[2px] transition-all">Bosing</button>

{/* Secondary (pink) */}
<button className="px-6 py-3 bg-[#FF9B9B] hover:bg-[#FF8888] text-white font-bold rounded-xl border-2 border-gray-900 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] ...">Ikkilamchi</button>

{/* Danger */}
<button className="px-6 py-3 bg-red-500 hover:bg-red-600 text-white font-bold rounded-xl border-2 border-gray-900 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] ...">O'chirish</button>

{/* Ghost */}
<button className="px-6 py-3 bg-white dark:bg-gray-800 text-gray-900 dark:text-white font-bold rounded-xl border-2 border-gray-900 hover:bg-gray-100 transition-colors">Bekor qilish</button>
```
O'lchamlar: `px-4 py-2 text-sm` (kichik), `px-6 py-3 text-base` (o'rta), `px-8 py-4 text-lg` (katta).

### Input maydonlari
```tsx
<input className="w-full px-4 py-3 border-2 border-gray-900 rounded-xl bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-400 transition-all" placeholder="Matn kiriting..." />

<textarea rows={4} className="... resize-none" />

<select className="... appearance-none cursor-pointer"><option>1</option></select>
```

### Badge / Tag
```tsx
<span className="inline-flex items-center gap-2 px-3 py-1 rounded-lg text-xs font-bold border-2 border-gray-900 bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400">Faol</span>
```

### Modal
```tsx
<div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
  <div className="bg-white dark:bg-dark-surface rounded-3xl p-8 max-w-md w-full border-2 border-gray-900 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
    <h3 className="text-2xl font-bold mb-4">Sarlavha</h3>
    <p className="text-gray-600 dark:text-gray-400 mb-6">Matn...</p>
    <div className="flex gap-3">
      <button className="flex-1 px-6 py-3 bg-gray-200 dark:bg-gray-700 font-bold rounded-xl border-2 border-gray-900">Bekor</button>
      <button className="flex-1 px-6 py-3 bg-linear-to-br from-[#38C9E6] to-[#43E8A0] text-white font-bold rounded-xl border-2 border-gray-900 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]">Tasdiqlash</button>
    </div>
  </div>
</div>
```

### Statistik karta (real misol)
```tsx
<Card3D className="p-6">
  <div className="flex items-start justify-between mb-4">
    <div className="flex-1">
      <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Jami foydalanuvchilar</p>
      <p className="text-5xl font-bold text-gray-900 dark:text-white mb-4">1,234</p>
    </div>
    <Icon3D gradient="cyan-blue" size="lg"><Users className="w-7 h-7 text-white" /></Icon3D>
  </div>
  <div className="flex items-center gap-2 text-sm">
    <TrendingUp className="w-4 h-4 text-green-600" />
    <span className="text-green-600 font-semibold">+12% bu oy</span>
  </div>
</Card3D>
```

### Bo'sh holat (Empty state)
```tsx
<div className="bg-white dark:bg-dark-surface border-2 border-gray-900 rounded-3xl p-12 text-center shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
  <Building2 className="w-16 h-16 mx-auto mb-4 text-gray-400" />
  <h3 className="text-xl font-bold mb-2">Hech narsa topilmadi</h3>
  <p className="text-gray-600 dark:text-gray-400">Filtrlarni o'zgartirib ko'ring</p>
</div>
```

### Navbar (asosiy tuzilma)
- `sticky top-0 z-50`, fon shaffof (`bg-transparent`)
- Scroll'da yashirinadi/ko'rinadi (`translate-y-0` / `-translate-y-full`)
- `max-w-7xl mx-auto px-4 sm:px-6 py-4`
- Tarkibiy qismlar: Logo, DesktopNav (markazda), o'ng tomonda LanguageSwitcher + ProfileMenu + ThemeToggle
- Mobil: hamburger menyu (`Menu`/`X` ikonlari, `lg:hidden`)

---

## 8. Loading va Skeleton

### Spinner (brend "21" bilan — o'z logotipingizga moslang)
```tsx
<div className="relative">
  <div className="w-12 h-12 rounded-full border-4 border-gray-200 dark:border-gray-700 absolute inset-0 animate-spin"
       style={{ borderTopColor: '#38C9E6', borderRightColor: '#43E8A0', animationDuration: '1s' }} />
  <div className="w-12 h-12 flex items-center justify-center relative z-10">
    <span className="text-2xl font-bold bg-linear-to-br from-[#38C9E6] to-[#43E8A0] bg-clip-text text-transparent font-montserrat">21</span>
  </div>
</div>
```

O'lchamlar: `sm: w-8 h-8`, `md: w-12 h-12`, `lg: w-16 h-16`, `xl: w-24 h-24`. FullScreen rejim: `fixed inset-0 z-50 bg-white/80 dark:bg-dark-page/80 backdrop-blur-sm`.

### Skeleton (asosiy)
```tsx
export function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse bg-gray-200 dark:bg-dark-surface rounded-2xl ${className}`} aria-hidden="true" />;
}
```
Tayyor variantlar: `CardSkeleton`, `ProfileHeaderSkeleton`, `TableRowSkeleton`, `StatsCardSkeleton`, `FormSkeleton`, `ListSkeleton`, `GridSkeleton`, `DashboardSkeleton`, `PageSkeleton`. Har biri bir xil 3D card stilini saqlaydi (`border-2 border-gray-900 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]`).

---

## 9. Animatsion fon (Squares)

Sahifa orqasida sekin harakatlanuvchi canvas to'r chiziqlari. `layout.tsx`'da `fixed inset-0 -z-10` bilan joylashtirilgan:

```tsx
<div className="fixed inset-0 -z-10 bg-gray-50 dark:bg-dark-page">
  <Squares
    direction="diagonal"
    speed={0.1}
    squareSize={60}
    borderColor="rgba(128, 128, 128, 0.08)"
    hoverFillColor="rgba(128, 128, 128, 0.03)"
  />
</div>
```

`Squares` — `<canvas>` asosidagi komponent. Props: `direction` (`diagonal`/`up`/`down`/`left`/`right`), `speed`, `squareSize`, `borderColor`, `hoverFillColor`. Sichqoncha ostidagi katak yoritiladi.

> To'liq kodi asl loyihaning `app/components/Squares.tsx` faylida. Boshqa platformaga shundayligicha ko'chirish mumkin.

### Maxsus scrollbar (gradient)
```css
::-webkit-scrollbar { width: 12px; height: 12px; }
::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #38C9E6 0%, #43E8A0 100%);
  border-radius: 10px;
  border: 2px solid rgba(0, 0, 0, 0.2);
}
::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
.dark ::-webkit-scrollbar-track { background: #2A3442; }
* { scrollbar-width: thin; scrollbar-color: #38C9E6 #f1f1f1; }
```

---

## 10. Responsive dizayn

### Grid layoutlar
```tsx
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">  {/* 1-2-3-4 */}
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">                 {/* 1-2-3 */}
<div className="grid grid-cols-1 md:grid-cols-2 gap-6">                                 {/* 1-2 */}
```

### Flex va ko'rinish
```tsx
<div className="flex flex-col lg:flex-row gap-6">   {/* mobil: ustun, desktop: qator */}
<div className="hidden lg:block">                   {/* faqat desktop */}
<div className="block lg:hidden">                   {/* faqat mobil */}
```

### Sahifa shabloni
```tsx
<div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
  <div className="max-w-7xl mx-auto">
    <div className="mb-12">
      <h1 className="text-4xl font-bold mb-3">Sahifa sarlavhasi</h1>
      <p className="text-gray-600 dark:text-gray-400 text-lg">Tavsif</p>
    </div>
    {/* kontent */}
  </div>
</div>
```

---

## 11. Eng yaxshi amaliyotlar

### ✅ QILING
- Doimo `border-2 border-gray-900` ishlating (bir xillik uchun)
- 3D soyalarni interaktiv elementlarga qo'llang
- Gradientni faqat **asosiy** harakatlar (primary action) uchun ishlating
- Har bir element turi uchun bir xil burchak radiusi: card → `rounded-3xl`, tugma → `rounded-xl`
- Barcha bosiladigan elementlarga hover holati qo'shing
- Har bir komponent uchun dark mode'ni qo'llang va sinab ko'ring
- Mobil-first yondashuv: avval mobil, keyin kattalashtiring

### ❌ QILMANG
- Bir ko'rinishda turli soya stillarini aralashtirmang
- Yupqa chegara (`border` yoki `border-1`) ishlatmang
- Interaktiv elementlarda hover holatini unutmang
- Juda ko'p turli gradient kombinatsiyalaridan foydalanmang
- Dark mode'ni e'tiborsiz qoldirmang
- Asosiy UI uchun o'tkir burchak (`rounded-none`) ishlatmang
- Navbar/sticky elementlarda `translate` ishlatmang (`card-3d-static` ishlating)

---

## 12. Boshqa platformaga ko'chirish

Yangi loyihada bu dizaynni qo'llash uchun:

1. **Tailwind CSS v4 o'rnating** (yoki mavjud Tailwind loyihangizdan foydalaning).

2. **`globals.css`'ga ko'chiring:**
   - `@theme { ... }` ichidagi barcha rang o'zgaruvchilari (3-bo'lim)
   - 3D soya klasslari: `.shadow-3d`, `.card-3d`, `.card-3d-static`, `.btn-3d` (5-bo'lim)
   - Gradient utility'lar: `.gradient-brand`, `.gradient-text`
   - Maxsus scrollbar stillari (9-bo'lim)
   - `@custom-variant dark (&:where(.dark, .dark *));`

3. **Shriftlarni ulang** — Montserrat (sarlavha) + IBM Plex Mono (matn) (4-bo'lim).

4. **Komponentlarni ko'chiring:** `Card3D`, `Button3D`, `Icon3D`, `ThemeProvider`, `ThemeToggle`, `LoadingSpinner`, `SkeletonLoader`, `Squares` (asl loyihaning `app/components/` papkasidan).

5. **Brendni o'zgartiring:** o'z platformangiz uchun `--color-brand-cyan` va `--color-brand-green` ni o'zgartiring — butun tizim avtomatik moslashadi. Logotip ("21") va spinner matnini ham yangilang.

6. **Layout o'rnating:** sahifa foniga `Squares` animatsiyasi + `dark:bg-dark-page`, ustiga Navbar va kontent.

### Brendni o'zgartirish misoli
```css
/* Eski (cyan-green) */
--color-brand-cyan:  #38C9E6;
--color-brand-green: #43E8A0;

/* Yangi (masalan, binafsha-pushti) */
--color-brand-cyan:  #8B5CF6;   /* asosiy */
--color-brand-green: #EC4899;   /* aksent */
```
Shundan keyin `.gradient-brand`, `.btn-3d`, scrollbar va barcha gradientlar yangi rangda ishlaydi. Faqat to'g'ridan-to'g'ri yozilgan `from-[#38C9E6] to-[#43E8A0]` klasslarini ham qidirib almashtiring (yoki ularni `gradient-brand` klassiga o'tkazing).

---

## 🎨 Tezkor shpargalka (Cheat Sheet)

```css
/* Card */
bg-white dark:bg-dark-bg rounded-3xl p-6 border-2 border-gray-900 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]

/* Primary tugma */
px-6 py-3 bg-linear-to-br from-[#38C9E6] to-[#43E8A0] text-white font-bold rounded-xl border-2 border-gray-900 shadow-[3px_3px_0px_0px_rgba(0,0,0,1)] hover:shadow-[5px_5px_0px_0px_rgba(0,0,0,1)] hover:-translate-x-[2px] hover:-translate-y-[2px] transition-all

/* Input */
w-full px-4 py-3 border-2 border-gray-900 rounded-xl bg-white dark:bg-gray-800 focus:ring-2 focus:ring-primary-400 transition-all

/* Badge */
inline-flex items-center gap-2 px-3 py-1 rounded-lg text-xs font-bold border-2 border-gray-900 bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400
```

---

**Manba:** CareerHub21 loyihasi (Next.js 16 + Tailwind v4)
**Uslub:** 3D Neo-Brutalism
**Tayyorlandi:** boshqa platformaga moslashtirish uchun
