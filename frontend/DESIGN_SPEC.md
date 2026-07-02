# DESIGN_SPEC — Peer Learn (3D Neo-Brutalist Dark)

> Bu hujjat MAJBURIY standart. HAR BIR sahifa va komponent shunga QAT'IY amal qilishi kerak.
> Maqsad: butun platforma **bir xil** ko'rinishi.

## 1. Tema: 3D Neo-Brutalist Dark

Asosiy belgilar: **qalin qora chegara** (`border-2 border-black`) + **qattiq ofset soya**
(`shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]`) + hoverda soya kichrayib bosilish effekti.

## 2. Ranglar (faqat shu hex'lar)

| Rol | Hex |
|-----|-----|
| Sahifa foni | `#1E2A38` |
| Karta / surface | `#2A3442` |
| Ichki element (elevated) | `#34495E` |
| Chegara | `#000000` (har doim) |
| Primary gradient | `from-[#38C9E6] to-[#43E8A0]` |
| Teal accent | `#38C9E6` |
| Mint accent | `#43E8A0` |
| Purple (secondary) | `#cdbdff` |
| Gold | `#ffd740` |
| Success | `#43E8A0` / `#00e676` |
| Error / danger | `#FF9B9B` |
| Matn (asosiy) | `#FFFFFF` |
| Matn (ikkilamchi) | `#B0BEC5` |

Yangi rang IXTIRO QILMANG. Faqat yuqoridagilar.

## 3. Tipografiya

- **Sarlavha (h1/h2), label, tugma matni:** `font-montserrat`, `font-black`/`font-extrabold`, ko'pincha `uppercase tracking-wider`.
- **Raqam / data / input / kod:** `font-ibm-plex-mono`.
- **Body matn:** `font-sans` (Inter).

## 4. Radius

- Karta / modal / katta panel: `rounded-3xl`
- Tugma / input / kichik panel / tab: `rounded-xl`
- Badge / rank / kichik pill: `rounded-lg`

## 5. Shared komponentlardan FOYDALANING (yangi yaratmang)

`@/shared/ui` dan: `PageHeader`, `Button`, `Card`, `Input`, `Select`, `Badge`,
`Avatar`, `Modal`, `Spinner`, `Skeleton`, `EmptyState`, `ProgressBar`.

- Tugma → `<Button variant="primary|secondary|ghost|danger">` (o'z tugmangizni yasamang).
- Karta → `<Card>` (yoki bir xil klasslar: `bg-[#2A3442] border-2 border-black rounded-3xl shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]`).
- Modal → `<Modal>`.

## 6. Sahifa qolipi (MAJBURIY)

Har bir sahifa AYNAN shu strukturada:

```tsx
import { PageHeader, /* ... */ } from '@/shared/ui';
import { SomeIcon } from 'lucide-react';

export default function XPage() {
  return (
    <div className="flex flex-col gap-6 animate-fade-in font-ibm-plex-mono text-white">
      <PageHeader
        title="Sahifa nomi"
        subtitle="Qisqa izoh."
        icon={SomeIcon}
        actions={/* ixtiyoriy o'ng tugmalar */}
      />

      {/* kontent: Card/grid/tab'lar */}
    </div>
  );
}
```

- Root div HAR DOIM: `flex flex-col gap-6 animate-fade-in font-ibm-plex-mono text-white`.
- Sarlavha HAR DOIM `<PageHeader />` orqali (qo'lda h1 yozmang).

## 7. Holatlar (state'lar) — MAJBURIY

Har bir ma'lumot yuklaydigan sahifa uchun 3 holat bo'lishi shart:
1. **Loading:** `Skeleton` (afzal) yoki `<Spinner />`.
2. **Error:** `isError` bo'lsa foydalanuvchiga ko'rinadigan xato bloki (`#FF9B9B` matn + qayta urinish yo'li). Silent failure MAN ETILADI.
3. **Empty:** ma'lumot bo'sh bo'lsa `<EmptyState />` yoki markazlashgan `Card`.

## 8. Interaktiv elementlar

- HAR bir tugma real `onClick`/submit'ga ega bo'lishi kerak (dekorativ/no-op tugma MAN ETILADI).
- Formalar `react-hook-form` + `zod` bilan.
- Hover/active: neo-brutalist press effekti (`hover:translate` + soya kichrayishi).

## 9. Taqiqlangan narsalar

- Yupqa `border` (1px) yoki `shadow-2xl`/`shadow-lg` (blur soya) — neo-brutalist EMAS.
- Eski palitra (`#18D6C7`, `#44EB99`, `#1E2330`, `#2A3040`) — ISHLATMANG.
- Yangi rang, yangi radius o'lchami, yangi shrift.
- Boshqa sahifadan farq qiladigan sarlavha uslubi.

## 10. Mobil / Responsive standart (MAJBURIY)

Ilova **mobile-first** bo'lishi kerak. Asosiy stillar mobil uchun, kattalari `sm:`/`md:`/`lg:` bilan.

Breakpoint'lar (Tailwind): `sm` 640px, `md` 768px, `lg` 1024px.
- `< lg` — mobil/planshet: pastda `BottomNav`, yuqorida `Header`.
- `>= lg` — desktop: yuqorida `Navbar`.

**Qoidalar:**
1. **Gorizontal overflow BO'LMASIN.** Uzun matn `truncate` yoki `break-words`. Keng jadval/qatorlar mobilda `overflow-x-auto` yoki ustma-ust (stack) bo'lsin.
2. **Touch target >= 44px** (`h-11` yoki `min-h-11`, `p-3`+). Kichik ikonka-tugmalar mobilda kattaroq bosiladigan zona bilan.
3. **Grid'lar:** mobilda `grid-cols-1` (yoki `grid-cols-2` kichik statlar), `sm:grid-cols-2`, `md:/lg:grid-cols-3/4`. Hech qачон mobilda 3+ ustun matnli karta.
4. **Padding/spacing:** mobil `p-4 gap-4`, `sm:p-6 gap-6`. Sarlavha mobil `text-xl`, `sm:text-2xl`.
5. **Modal:** mobilda deyarli to'liq kenglik (`w-full max-w-[...]` + `p-4`), ekranga sig'sin (`max-h-[90vh] overflow-y-auto`).
6. **Flex qatorlar** (masalan header ichidagi title + tugma): mobilda `flex-col`, `sm:flex-row`. Tugmalar mobilda `w-full`, `sm:w-auto`.
7. **Matn o'lchami:** mobilda o'qilishi uchun asosiy matn `text-sm` dan kichik bo'lmasin (yordamchi `text-xs` mumkin).
8. **Rasm/avatar/statlar** mobilda kichrayadi, lekin bosiladigan zona saqlanadi.
9. **`pb-28 lg:pb-8`** — mobilda BottomNav ustidan kontent ko'rinishi uchun pastki padding (AppLayout allaqachon beradi, lekin sahifa ichidagi sticky element'larга e'tibor bering).
10. Har bir sahifani **360px kenglikda** (kichik telefon) sinab ko'ring — hech narsa kesilmasin, chiqib ketmasin.

**Shared UI komponentlari (`@/shared/ui`) ni O'ZGARTIRMANG** — ular allaqachon responsive. Faqat sahifa/feature ichidagi layout'ni moslang.

