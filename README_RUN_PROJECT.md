# OLX.UZ Backend loyihasini ishga tushirish qo‘llanmasi

Ushbu  loyihani ishga tushirish uchun qo'llanma.

## 1. Talab qilinadigan dasturlar

Kompyuterda quyidagilar o‘rnatilgan bo‘lishi kerak:

- Python 3.11 yoki 3.10
- PostgreSQL 14+
- Git
- Telegram bot token (agar bot qismini ham ishlatmoqchi bo‘lsangiz)

Versiyalarni tekshirish uchun:

```bash
python --version
pip --version
git --version
psql --version
```

## 2. Loyihani clone qilish

Repository ni yuklab oling:

```bash
git clone <REPOSITORY_URL>
cd <PROJECT_FOLDER>
```

## 3. Virtual environment yaratish

### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```


### Windows Git Bash

```bash
python -m venv venv
source venv/Scripts/activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

Aktivatsiyadan keyin terminal boshida `(venv)` chiqishi kerak.

## 4. Kutubxonalarni o‘rnatish



```bash
pip install -r requirements.txt
```



## 5. `.env` fayl yaratish

Project root papkada `.env.example` dan nusxa olib `.env` yarating:

```bash
cp .env.example .env
```


`.env` ichida quyidagi qiymatlarni to‘ldiring:

```env

DB_NAME=olx_db
DB_USER=olx_user
DB_PASSWORD=olx_pass_123
DB_HOST=127.0.0.1
DB_PORT=5432

TELEGRAM_BOT_TOKEN=your-bot-token
BACKEND_BASE_URL=http://127.0.0.1:8000

DEBUG=1
```

## 6. PostgreSQL database yaratish

PostgreSQL ga kiring:

```bash
psql -U postgres
```

Keyin quyidagi SQL buyruqlarni bajaring:

```sql
CREATE DATABASE olx_db;
CREATE USER olx_user WITH PASSWORD 'olx_pass_123';
GRANT ALL PRIVILEGES ON DATABASE olx_db TO olx_user;
```

Keyin database ichiga o‘ting:

```sql
\c olx_db
```

Va schema uchun ruxsat bering:

```sql
GRANT USAGE, CREATE ON SCHEMA public TO olx_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO olx_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO olx_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO olx_user;
```

Chiqish:

```sql
\q
```

## 7. Migratsiyalarni bajarish

Project root papkada:

```bash
python manage.py makemigrations
python manage.py migrate
```

Agar hammasi to‘g‘ri bo‘lsa, migrationlar muvaffaqiyatli ishlaydi.

## 8. Superuser yaratish

Admin panel uchun:

```bash
python manage.py createsuperuser
```

Login, email va password kiriting.

## 9. Backend serverni ishga tushirish

```bash
python manage.py runserver 127.0.0.1:8000
```

Server ishga tushgach quyidagi URL lar ishlaydi:

- Swagger: `http://127.0.0.1:8000/api/docs/`
- Schema: `http://127.0.0.1:8000/api/schema/`
- Admin panel: `http://127.0.0.1:8000/admin/`

## 10. Telegram botni ishga tushirish

Agar bot qismi ham kerak bo‘lsa, yangi terminal oching, virtual environment ni yoqing va quyidagini bajaring:

```bash
python bot/main.py
```

Telegram bot ichida:

- `/start` — login yoki register
- `/me` — profilni ko‘rish
- `/upgrade_seller` — seller bo‘lish
- `/logout` — logout

Muhim: backend server oldin ishga tushgan bo‘lishi kerak.

## 11. API ni test qilish

Swagger orqali test qilish tavsiya etiladi:

1. `POST /api/v1/auth/telegram-login/`
2. `GET /api/v1/users/me/`
3. `POST /api/v1/users/me/upgrade-to-seller/`
4. `POST /api/v1/products/`
5. `POST /api/v1/products/{id}/publish/`
6. `GET /api/v1/products/`
7. `POST /api/v1/favorites/`
8. `POST /api/v1/orders/`
9. `PATCH /api/v1/orders/{id}/`
10. `POST /api/v1/reviews/`

## 12. Media fayllar

Mahsulot rasmlari va avatarlar `media/` papkaga saqlanadi. Development rejimida Django ularni avtomatik serve qiladi.

## 13. Loyiha strukturasining asosiy qismlari

```text
config/          # settings, urls
users/           # custom user, auth, profile
marketplace/     # category, product, favorites, orders, reviews
bot/             # telegram bot
media/           # upload qilingan rasmlar
manage.py
.env.example
README.md
```

## 14. Eng ko‘p uchraydigan xatolar

### 1. `ModuleNotFoundError`
Kerakli kutubxona o‘rnatilmagan.

Yechim:

```bash
pip install -r requirements.txt
```

### 2. `password authentication failed for user`
`.env` dagi PostgreSQL login yoki password noto‘g‘ri.

### 3. `permission denied for schema public`
Database user ga schema uchun ruxsat berilmagan.

Yechim: 6-bosqichdagi `GRANT` buyruqlarini qayta bajaring.

### 4. `Connection refused`
Backend server ishlamayapti yoki noto‘g‘ri portda turibdi.

Tekshiring:

```bash
python manage.py runserver 127.0.0.1:8000
```

### 5. Bot backendga ulanolmayapti
`.env` ichidagi `BACKEND_BASE_URL` noto‘g‘ri bo‘lishi mumkin.

To‘g‘ri qiymat:

```env
BACKEND_BASE_URL=http://127.0.0.1:8000
```

## 15. Ishni tugatgandan keyin

Agar yangi kutubxonalar o‘rnatilgan bo‘lsa:

```bash
pip freeze > requirements.txt
```

## 16. Xavfsizlik

`.env` faylni GitHub ga push qilmang.

`.gitignore` ichida kamida quyidagilar bo‘lsin:

```gitignore
.env
venv/
__pycache__/
*.pyc
media/
```

## 17. Qisqa start ketma-ketligi

Agar hammasi tayyor bo‘lsa, keyingi safar loyihani ishga tushirish uchun faqat shu kifoya:

### Backend

```bash
source venv/Scripts/activate   # Windows Git Bash
python manage.py runserver 127.0.0.1:8000
```

### Bot

Yangi terminal:

```bash
source venv/Scripts/activate
python bot/main.py
```

---

Agar project birinchi marta ishga tushirilayotgan bo‘lsa, 3-bosqichdan 9-bosqichgacha hammasini ketma-ket bajarish kerak.
