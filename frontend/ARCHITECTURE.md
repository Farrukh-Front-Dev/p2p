# Frontend Arxitekturasi

Peer Learn frontend **feature-based (feature-sliced)** arxitekturada qurilgan.
Kod uch qatlamga bo'lingan: `app/`, `features/`, `shared/`.

```
src/
├── main.tsx                 # Ilova kirish nuqtasi (index.html shuni yuklaydi)
├── index.css                # Global stillar / Tailwind @theme tokenlari
│
├── app/                     # ILOVA QOBIG'I (application shell)
│   ├── App.tsx              # Provider'lar (React Query, ErrorBoundary, Router)
│   ├── router.tsx           # Marshrutlar (lazy-loaded sahifalar)
│   ├── ErrorBoundary.tsx    # Global xatolarni ushlash
│   └── layout/              # AppLayout, Navbar, Sidebar, Header, BottomNav
│
├── features/                # DOMEN MODULLARI — har biri mustaqil
│   ├── auth/
│   │   ├── api.ts           # server chaqiriqlari (authService)
│   │   ├── hooks.ts         # React Query hooklari (useAuth)
│   │   ├── store.ts         # zustand store (useAuthStore)
│   │   ├── components/      # AuthGuard, GuestGuard
│   │   ├── pages/           # LoginPage
│   │   └── index.ts         # feature'ning ochiq API'si (public barrel)
│   ├── onboarding/  · dashboard/ · slots/ · reviews/ · profile/
│   ├── search/ · leaderboard/ · notifications/ · settings/
│   │   (har birida: api.ts, hooks.ts, components/, pages/, index.ts)
│
└── shared/                  # QAYTA ISHLATILUVCHI, domendan xoli kod
    ├── ui/                  # dizayn tizimi (Button, Card, Modal, ...)
    ├── lib/                 # axios, utils, mockDb (offline demo)
    ├── hooks/               # umumiy hooklar (useWebSocket)
    ├── stores/              # global store'lar (toast, theme)
    └── types/               # umumiy TypeScript tiplari (api.ts)
```

## Qoidalar (bog'liqlik yo'nalishi)

1. **`app` -> `features` -> `shared`** — bir tomonlama.
   - `app` istalgan `feature` va `shared`dan foydalanishi mumkin.
   - `feature` faqat `shared`dan (va o'z ichidan) foydalanadi.
   - `shared` hech qachon `feature` yoki `app`ga bog'liq bo'lmaydi.
2. **Feature'lar orasidagi import** faqat feature'ning `index.ts` public API'si orqali
   bo'lishi kerak (masalan `@/features/slots`), ichki fayllarga to'g'ridan-to'g'ri emas.
3. **Sahifalar** router'da `lazy()` bilan to'g'ridan-to'g'ri fayl yo'li orqali import
   qilinadi (`@/features/auth/pages/LoginPage`) — code-splitting saqlanadi.
4. Barcha importlar `@/` alias orqali (`@` -> `src/`), nisbiy `../../` yo'llardan qochiladi.

## Har bir feature'ning tuzilishi

| Fayl / papka   | Vazifasi                                             |
|----------------|------------------------------------------------------|
| `api.ts`       | Backend endpointlariga so'rovlar (axios)             |
| `hooks.ts`     | React Query query/mutation hooklari                  |
| `store.ts`     | (ixtiyoriy) zustand mahalliy holati                  |
| `components/`  | Faqat shu feature ichida ishlatiladigan komponentlar |
| `pages/`       | Route'ga ulanadigan sahifa komponentlari             |
| `index.ts`     | Feature'ning ochiq (public) API'si                   |
