# Requirements Document

## Introduction

PeerLearn Bot — School 21 talabalari uchun peer-to-peer (p2p) bilim almashish platformasi bo'lib, Telegram bot orqali ishlaydi. Foydalanuvchilar o'z bilimlarini ulashish uchun slot ochadi (mentor) yoki boshqalardan o'rganish uchun slot band qiladi (mentee). Bot ikki tarafni anonim tarzda birlashtiradi va sessiya boshlanishidan oldin kimligini oshkor qiladi. Tizimda coin (tanga), XP va daraja (level) mexanikalari mavjud.

Ushbu hujjat backend qismi uchun talablarni belgilaydi: ma'lumotlar bazasi modellari, autentifikatsiya, slot va sessiya boshqaruvi, coin/XP tizimi, eslatma scheduleri, anonim ulanish va xabar relay tizimi.

Texnologik stack: Python 3.11+, aiogram 3.x, FastAPI, SQLAlchemy 2.x (async), Alembic, PostgreSQL, Redis, APScheduler, httpx, Pydantic v2.

### School 21 API (haqiqiy/tasdiqlangan)

PRD'dagi GraphQL taxminidan farqli o'laroq, School 21 platformasi **REST API + Keycloak** ishlatadi. Quyidagi oqim haqiqiy credentiallar bilan tekshirilgan va ishlaydi:

- **Autentifikatsiya (Keycloak, Resource Owner Password Grant):**
  - Token endpoint: `https://auth.21-school.ru/auth/realms/EduPowerKeycloak/protocol/openid-connect/token`
  - Parametrlar: `client_id=s21-open-api`, `grant_type=password`, `username`, `password`
  - Javob: `access_token` (Bearer, `expires_in` ≈ 36000s), `refresh_token`, `refresh_expires_in`
  - JWT `access_token` ichida: `preferred_username`, `given_name`, `family_name`, `name`, `email`
- **Profil (REST, Bearer token bilan):**
  - `GET https://platform.21-school.ru/services/21-school/api/v1/participants/{login}` → `login`, `className`, `parallelName`, `expValue`, `level`, `expToNextLevel`, `campus` (`id`, `shortName`), `status`
  - `GET .../participants/{login}/skills` → `skills[]` (`name`, `points`) — yo'nalishlarni avtomatik taklif qilish uchun
  - `GET .../participants/{login}/coalition` → `coalitionId`, `name`, `rank`
  - `GET .../participants/{login}/workstation` → ish stansiyasi ma'lumotlari

> **Eslatma:** School 21 avatar/URL maydoni ushbu participants endpointida qaytmaydi. `avatar_url` maydoni ixtiyoriy bo'lib qoladi (kelajakda boshqa endpointdan to'ldirilishi mumkin).

## Glossary

- **Mentor** — slot ochib, o'z bilimini o'rgatuvchi foydalanuvchi.
- **Mentee** — mavjud slotni band qilib, o'rganuvchi foydalanuvchi.
- **Slot** — mentor tomonidan belgilangan vaqt oralig'i va yo'nalish.
- **Session (Sessiya)** — band qilingan slot boshlanganda yaratiladigan faol o'qish jarayoni.
- **Coin (Tanga)** — slot band qilish uchun sarflanadigan va o'rgatish uchun olinadigan ichki valyuta.
- **XP** — sessiyalar uchun beriladigan tajriba ballari.
- **Reveal (Oshkor qilish)** — sessiya boshlanishidan oldin tomonlarning kimligini ma'lum qilish.

---

## Requirements

### Requirement 1: Foydalanuvchi autentifikatsiyasi va ro'yxatdan o'tish

**User Story:** School 21 talabasi sifatida, men o'z School 21 hisobim orqali ro'yxatdan o'tmoqchiman, toki platformadan foydalana olishim uchun.

#### Acceptance Criteria

1. WHEN foydalanuvchi birinchi marta `/start` buyrug'ini yuborsa THEN tizim SHALL ro'yxatdan o'tish jarayonini boshlashi va School 21 login so'rashi kerak.
2. WHEN foydalanuvchi School 21 login va parolini kiritsa THEN tizim SHALL Keycloak token endpoint (`auth.21-school.ru`, `client_id=s21-open-api`, `grant_type=password`) orqali hisob ma'lumotlarini tekshirishi kerak.
3. IF School 21 autentifikatsiyasi muvaffaqiyatsiz bo'lsa (HTTP 401 yoki `error` qaytsa) THEN tizim SHALL xato xabarini ko'rsatishi va jarayonni qaytadan boshlashga imkon berishi kerak.
4. WHEN foydalanuvchi parolini kiritsa THEN tizim SHALL parol xabarini xavfsizlik uchun chatdan o'chirishi va parolni hech qayerda saqlamasligi kerak.
5. WHEN autentifikatsiya muvaffaqiyatli bo'lsa THEN tizim SHALL `access_token` orqali `GET /participants/{login}` endpointidan profil ma'lumotlarini (`login`, `level`, `expValue`, `campus`) olishi kerak.
6. WHEN profil ma'lumotlari olinsa THEN tizim SHALL foydalanuvchidan kamida 1 ta va ko'pi bilan 5 ta yo'nalish tanlashni so'rashi kerak.
7. WHERE foydalanuvchi `skills` ma'lumotlari mavjud bo'lsa THE tizim SHALL eng yuqori ball to'plagan skill'lar asosida yo'nalishlarni avtomatik taklif qilishi (preselect) mumkin.
8. WHEN ro'yxatdan o'tish yakunlansa THEN tizim SHALL yangi foydalanuvchini `DEFAULT_COINS` (5) tanga bilan yaratishi va `school21_login`, `level`, `xp` qiymatlarini saqlashi kerak.
9. WHEN allaqachon ro'yxatdan o'tgan faol foydalanuvchi `/start` yuborsa THEN tizim SHALL uni bosh menyuga yo'naltirishi kerak (ro'yxatdan o'tishni takrorlamasdan).
10. IF foydalanuvchi yo'nalish tanlamasdan tasdiqlashga urinsa THEN tizim SHALL kamida bitta yo'nalish tanlash kerakligini bildirishi kerak.
11. THE tizim SHALL School 21 `access_token`/`refresh_token` larni xavfsiz saqlamasligi yoki faqat zarur bo'lganda Redis'da TTL bilan vaqtinchalik saqlashi kerak (parolni esa umuman saqlamaslik).

### Requirement 2: Slot ochish (Mentor)

**User Story:** Mentor sifatida, men o'rgatish uchun slot ochmoqchiman, toki boshqa talabalar mendan o'rganishi uchun.

#### Acceptance Criteria

1. WHEN ro'yxatdan o'tgan foydalanuvchi slot ochishni boshlasa THEN tizim SHALL yo'nalish tanlashni so'rashi kerak.
2. WHEN mentor yo'nalish tanlasa THEN tizim SHALL boshlanish vaqtini tanlashni so'rashi kerak.
3. WHEN mentor boshlanish vaqtini tanlasa THEN tizim SHALL tugash vaqtini tanlashni so'rashi kerak.
4. IF tugash vaqti boshlanish vaqtidan oldin yoki teng bo'lsa THEN tizim SHALL slotni yaratmasligi va xato bildirishi kerak.
5. IF boshlanish vaqti o'tmishda bo'lsa THEN tizim SHALL slotni yaratmasligi va xato bildirishi kerak.
6. WHEN mentor slot ma'lumotlarini tasdiqlasa THEN tizim SHALL slotni `open` statusi bilan yaratishi kerak.
7. WHEN slot yaratilsa THEN tizim SHALL slotning `mentor_id` maydonini joriy foydalanuvchiga bog'lashi kerak.
8. WHEN slot muvaffaqiyatli yaratilsa THEN tizim SHALL mentorga tasdiqlovchi xabar yuborishi kerak.

### Requirement 3: Slot band qilish (Mentee)

**User Story:** Mentee sifatida, men mavjud slotni band qilmoqchiman, toki tanlagan yo'nalishimda o'rganish imkoniga ega bo'lishim uchun.

#### Acceptance Criteria

1. WHEN foydalanuvchi slot band qilishni boshlasa THEN tizim SHALL foydalanuvchining tanga miqdorini tekshirishi kerak.
2. IF foydalanuvchining tangasi 1 dan kam bo'lsa THEN tizim SHALL band qilishni bloklashi va yetarli tanga yo'qligini bildirishi kerak.
3. WHEN foydalanuvchi yo'nalish tanlasa THEN tizim SHALL faqat `open` statusidagi va o'ziga tegishli bo'lmagan slotlarni ko'rsatishi kerak.
4. WHILE slotlar ko'rsatilayotganda THE tizim SHALL mentor kimligini yashirishi (anonim) kerak.
5. IF tanlangan yo'nalishda ochiq slotlar bo'lmasa THEN tizim SHALL bo'sh holatni bildiruvchi xabar ko'rsatishi kerak.
6. WHEN foydalanuvchi slotni tanlab tasdiqlasa THEN tizim SHALL slotni atomik tarzda band qilishi (`booked` status, `mentee_id` o'rnatish) kerak.
7. IF slot tasdiqlash paytida boshqa foydalanuvchi tomonidan band qilingan bo'lsa THEN tizim SHALL band qilishni rad etishi va xato bildirishi kerak.
8. WHEN slot muvaffaqiyatli band qilinsa THEN tizim SHALL mentee dan 1 tanga ayirishi va tranzaksiyani yozib qo'yishi kerak.
9. WHEN slot band qilinsa THEN tizim SHALL mentorga (mentee kimligini oshkor qilmasdan) xabar yuborishi kerak.

### Requirement 4: Anonim eslatma va kimligini oshkor qilish

**User Story:** Ishtirokchi sifatida, men sessiyadan oldin eslatma va sherigimning kimligini bilmoqchiman, toki sessiyaga tayyorlanishim uchun.

#### Acceptance Criteria

1. WHEN slot boshlanishigacha `REMINDER_MINUTES` (15) daqiqa qolsa THEN tizim SHALL ikkala tomonga eslatma yuborishi kerak.
2. WHEN eslatma yuborilsa THEN tizim SHALL mentor va mentee kimligini bir-biriga oshkor qilishi kerak.
3. WHEN eslatma yuborilsa THEN tizim SHALL slotning `reminder_sent` maydonini `true` qilib belgilashi kerak.
4. WHILE bir slot uchun eslatma allaqachon yuborilgan bo'lsa THE tizim SHALL takroriy eslatma yubormasligi kerak.
5. WHEN slot boshlanish vaqti kelsa THEN tizim SHALL sessiyani boshlashi kerak.

### Requirement 5: Sessiya boshqaruvi va chat ulanishi

**User Story:** Ishtirokchi sifatida, men sessiya boshlanganda sherigim bilan muloqot qila olmoqchiman, toki bilim almashishimiz uchun.

#### Acceptance Criteria

1. WHEN slot boshlanish vaqti kelsa THEN tizim SHALL sessiya yozuvini yaratishi va slotni `active` statusiga o'tkazishi kerak.
2. THE tizim SHALL aloqa kanalini abstrakt `ChatService` interfeysi orqali o'rnatishi kerak (implementatsiya almashtirilsa, qolgan kod o'zgarmasligi uchun).
3. THE tizim SHALL `ChatService` ning kamida ikki implementatsiyasini qo'llab-quvvatlashi kerak: `RelayChatService` (MVP, standart) va kelajakdagi `UserBotChatService` (haqiqiy guruh).
4. WHERE `RelayChatService` ishlatilsa THE tizim SHALL bir tomondan kelgan xabarni (matn, rasm, fayl, ovozli) ikkinchi tomonga bot orqali yetkazishi kerak.
5. WHEN sessiya boshlansa THEN tizim SHALL ikkala tomonga sessiya boshlangani haqida xabar yuborishi va relay rejimi yoqilganini bildirishi kerak.
6. WHILE sessiya faol bo'lsa THE tizim SHALL Redis'da relay bog'lanishini (`relay:{session_id}` → ikki user_id) saqlashi kerak.
7. IF aloqa kanalini o'rnatish muvaffaqiyatsiz bo'lsa THEN tizim SHALL xatoni log qilishi va tomonlarga bildirishi kerak.
8. WHEN sessiya yakunlansa THEN tizim SHALL relay bog'lanishini (yoki guruhni) tozalashi/yopishi kerak.

### Requirement 6: Sessiyani yakunlash va baholash

**User Story:** Ishtirokchi sifatida, men sessiyani yakunlab, sherigimga fikr-mulohaza qoldirmoqchiman, toki sessiya yopilib, mukofotlar berilishi uchun.

#### Acceptance Criteria

1. WHEN ishtirokchi `/finish` buyrug'ini yuborsa THEN tizim SHALL uning faol sessiyasi borligini tekshirishi kerak.
2. IF foydalanuvchida faol sessiya bo'lmasa THEN tizim SHALL faol sessiya yo'qligini bildirishi kerak.
3. WHEN foydalanuvchi yakunlashni tasdiqlasa THEN tizim SHALL undan izoh (kamida 10 belgi) yozishni so'rashi kerak.
4. IF izoh 10 belgidan qisqa bo'lsa THEN tizim SHALL izohni qabul qilmasligi va qaytadan so'rashi kerak.
5. WHEN bir tomon yakunlashni tasdiqlasa THEN tizim SHALL uning tasdig'ini saqlashi va ikkinchi tomon tasdig'ini kutishi kerak.
6. WHEN ikkala tomon ham sessiyani tasdiqlasa THEN tizim SHALL sessiyani `finished` statusiga o'tkazishi kerak.
7. WHEN sessiya yakunlansa THEN tizim SHALL ishtirokchilar qoldirgan izohlar va baholarni `reviews` jadvaliga saqlashi kerak.

### Requirement 7: Coin (Tanga) tizimi

**User Story:** Foydalanuvchi sifatida, men o'rgatganim uchun tanga olmoqchiman va o'rganish uchun tanga sarflamoqchiman, toki tizim adolatli almashinuvni ta'minlashi uchun.

#### Acceptance Criteria

1. WHEN slot band qilinsa THEN tizim SHALL mentee dan darhol 1 tanga ayirishi kerak.
2. WHEN sessiya ikkala tomon tomonidan yakunlansa THEN tizim SHALL mentorga `COIN_PER_SESSION` (1) tanga qo'shishi kerak.
3. IF mentor tangasi `MAX_COINS` (15) ga teng bo'lsa THEN tizim SHALL tangalarni `MAX_COINS` dan oshirmasligi kerak.
4. WHEN tanga miqdori o'zgarsa THEN tizim SHALL `transactions` jadvaliga yozuv qo'shishi kerak (turi va miqdori bilan).
5. WHILE bir sessiya uchun tanga allaqachon o'tkazilgan bo'lsa THE tizim SHALL takroriy mukofot bermasligi kerak (`coins_transferred` bayrog'i orqali).
6. WHERE foydalanuvchi tangasi 0 ga teng bo'lsa THE tizim SHALL o'rganish (band qilish) imkoniyatini bloklashi kerak.

### Requirement 8: XP va daraja (Level) tizimi

**User Story:** Foydalanuvchi sifatida, men sessiyalar uchun XP va darajalar olmoqchiman, toki o'sishimni kuzata olishim uchun.

#### Acceptance Criteria

1. WHEN sessiya yakunlansa THEN tizim SHALL mentorga `XP_PER_SESSION` (50) XP berishi kerak.
2. WHEN sessiya yakunlansa THEN tizim SHALL mentee ga `XP_PER_SESSION` ning yarmini (25) XP berishi kerak.
3. WHEN foydalanuvchi XP olsa THEN tizim SHALL uning umumiy XP siga ko'ra darajasini qayta hisoblashi kerak (XP jadvali asosida).
4. IF foydalanuvchi yangi darajaga o'tsa THEN tizim SHALL foydalanuvchiga daraja oshgani haqida xabar berishi kerak.
5. WHILE bir sessiya uchun XP allaqachon berilgan bo'lsa THE tizim SHALL takroriy XP bermasligi kerak (`xp_awarded` bayrog'i orqali).
6. WHEN mentor sessiyani yakunlasa THEN tizim SHALL uning `total_taught` hisobini 1 ga oshirishi kerak.
7. WHEN mentee sessiyani yakunlasa THEN tizim SHALL uning `total_learned` hisobini 1 ga oshirishi kerak.

### Requirement 9: Profil va statistika ko'rsatish

**User Story:** Foydalanuvchi sifatida, men o'z profilim va statistikamni ko'rmoqchiman, toki yutuqlarim va resurslarimni kuzata olishim uchun.

#### Acceptance Criteria

1. WHEN foydalanuvchi profilni so'rasa THEN tizim SHALL uning nickname, reyting, daraja, XP va tangalarini ko'rsatishi kerak.
2. WHEN profil ko'rsatilsa THEN tizim SHALL o'rgatgan va o'rgangan sessiyalar sonini ko'rsatishi kerak.
3. WHEN profil ko'rsatilsa THEN tizim SHALL foydalanuvchining yo'nalishlarini va keyingi darajagacha qolgan XP ni ko'rsatishi kerak.

### Requirement 10: Ko'p tillilik (i18n)

**User Story:** Foydalanuvchi sifatida, men botdan o'z tilimda foydalanmoqchiman, toki interfeysni tushunishim oson bo'lishi uchun.

#### Acceptance Criteria

1. WHERE foydalanuvchi tili `uz`, `ru` yoki `en` bo'lsa THE tizim SHALL barcha interfeys matnlarini shu tilda ko'rsatishi kerak.
2. WHEN foydalanuvchi tilni o'zgartirsa THEN tizim SHALL keyingi xabarlarni yangi tilda ko'rsatishi kerak.
3. IF tarjima topilmasa THEN tizim SHALL standart til (`uz`) ga qaytishi kerak.

### Requirement 11: Eslatma scheduleri (Background jobs)

**User Story:** Tizim operatori sifatida, men eslatmalar va sessiya boshlanishi avtomatik ishlashini istayman, toki qo'lda aralashuv kerak bo'lmasligi uchun.

#### Acceptance Criteria

1. WHEN bot ishga tushsa THEN tizim SHALL slotlarni har 1 daqiqada tekshiruvchi scheduler ishga tushirishi kerak.
2. WHEN scheduler ishlasa THEN tizim SHALL eslatma talab qiladigan va boshlanishi kerak bo'lgan slotlarni aniqlashi kerak.
3. WHERE bot qayta ishga tushsa THE tizim SHALL Redis jobstore orqali rejalashtirilgan vazifalarni saqlab qolishi kerak.
4. IF eslatma yoki sessiya boshlash jarayonida xato yuz bersa THEN tizim SHALL xatoni log qilishi va boshqa slotlarga ta'sir qilmasligi kerak.

### Requirement 12: Ma'lumotlar bazasi va migratsiyalar

**User Story:** Dasturchi sifatida, men ma'lumotlar bazasi sxemasi versiyalanishini va migratsiyalar orqali boshqarilishini istayman, toki sxema o'zgarishlari xavfsiz qo'llanilishi uchun.

#### Acceptance Criteria

1. THE tizim SHALL `users`, `slots`, `sessions`, `transactions`, `reviews` jadvallarini PRD sxemasiga muvofiq belgilashi kerak.
2. THE tizim SHALL barcha jadval o'zgarishlarini Alembic migratsiyalari orqali boshqarishi kerak.
3. THE tizim SHALL PostgreSQL ga async ulanish (asyncpg) orqali murojaat qilishi kerak.
4. WHERE so'rovlar tez-tez ishlatiladigan ustunlar (status, direction, start_time, mentor_id) bo'yicha bo'lsa THE tizim SHALL tegishli indekslarni yaratishi kerak.

### Requirement 13: Konfiguratsiya va deploy

**User Story:** Tizim operatori sifatida, men botni turli muhitlarda (development/production) ishga tushirmoqchiman, toki uni oson joylashtira olishim uchun.

#### Acceptance Criteria

1. THE tizim SHALL barcha sozlamalarni muhit o'zgaruvchilari (`.env`) orqali yuklashi kerak.
2. WHERE `DEBUG` rejimi yoqilgan bo'lsa THE tizim SHALL polling rejimida ishlashi kerak.
3. WHERE `DEBUG` rejimi o'chirilgan bo'lsa THE tizim SHALL webhook rejimida (FastAPI) ishlashi kerak.
4. THE tizim SHALL Docker va Docker Compose orqali (bot, postgres, redis) ishga tushirilishi mumkin bo'lishi kerak.
5. IF majburiy muhit o'zgaruvchisi yetishmasa THEN tizim SHALL ishga tushishda aniq xato bilan to'xtashi kerak.

### Requirement 14: Anti-spam va xavfsizlik

**User Story:** Tizim operatori sifatida, men botni spam va noto'g'ri foydalanishdan himoya qilmoqchiman, toki tizim barqaror ishlashi uchun.

#### Acceptance Criteria

1. WHEN foydalanuvchi qisqa vaqt ichida juda ko'p so'rov yuborsa THEN tizim SHALL throttling middleware orqali so'rovlarni cheklashi kerak.
2. WHEN foydalanuvchi parol kiritsa THEN tizim SHALL parolni saqlamasligi va xabarni o'chirishi kerak.
3. WHERE har bir so'rov kelganda THE tizim SHALL auth middleware orqali foydalanuvchi holatini tekshirishi kerak.
4. WHERE foydalanuvchi ro'yxatdan o'tmagan bo'lsa THE tizim SHALL faqat `/start` va ro'yxatdan o'tish jarayoniga ruxsat berishi kerak.
