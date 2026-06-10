# Kamchin Map - اصلاح نقشه بدون وابستگی مستقیم مرورگر به map.ir

## مشکل اصلی

API داخلی پروژه سالم است؛ وقتی `/api/v1/markets` وضعیت `200` می‌دهد، FastAPI و دیتابیس کار می‌کنند. خطای اصلی از کاشی‌های نقشه است. قبلاً مرورگر مستقیم به `map.ir` وصل می‌شد و در شبکه‌هایی که دسترسی مستقیم/route/DNS مشکل دارد، فایل‌هایی مثل `805.png` و `806.png` fail می‌شدند.

## اصلاح انجام‌شده

مسیر دریافت tile عوض شد:

```text
Browser -> FastAPI -> map.ir / OSM
```

مرورگر دیگر مستقیم `map.ir` را صدا نمی‌زند و API key داخل JavaScript نیست.

## فایل‌های مهم تغییرکرده

- `app/api/map_tile_router.py`
- `app/main.py`
- `app/core/config.py`
- `app/static/js/map.js`
- `app/templates/index.html`
- `.env`
- `requirements.txt`

## تست سریع

بعد از نصب dependencyها و اجرای سرور:

```bash
pip install -r requirements.txt
python run.py
```

این URL را در مرورگر باز کن:

```text
http://127.0.0.1:8000/api/v1/map/health
```

بعد این tile را تست کن:

```text
http://127.0.0.1:8000/api/v1/map/tiles/mapir/11/1316/805.png
```

اگر عکس برگشت، نقشه با provider اصلی درست است.

اگر خطای `502` برگشت، یعنی خود backend هم از شبکه فعلی به provider نقشه دسترسی ندارد. در این حالت باید یکی از این سه راه انجام شود:

1. `MAP_HTTP_PROXY` و `MAP_HTTPS_PROXY` برای backend تنظیم شود.
2. backend روی سروری اجرا شود که به map.ir دسترسی دارد.
3. tileها یک بار با اتصال سالم cache شوند و بعداً از cache داخلی خوانده شوند.

## تنظیمات `.env`

```env
MAP_DEFAULT_PROVIDER=mapir
MAPIR_API_KEY=...
MAP_TILE_CACHE_ENABLED=true
MAP_TILE_CACHE_DIR=./data/tile_cache
MAP_TILE_TIMEOUT_SECONDS=6
MAP_MAX_ZOOM=19
MAP_HTTP_PROXY=
MAP_HTTPS_PROXY=
```

## نکته cache مرورگر

در `index.html` نسخه script به `map.js?v=4` تغییر کرده تا مرورگر فایل قدیمی را از cache اجرا نکند.
