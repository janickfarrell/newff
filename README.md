# BarReplay Forex Factory News Pipeline

پروژه آماده GitHub برای دریافت تقویم اقتصادی Forex Factory در **GMT+0**، انتشار در Hugging Face Dataset و ارائه فایل `news.csv` از طریق Cloudflare Worker به اکسپرت BarReplay.

## معماری

`Forex Factory → GitHub Actions → Hugging Face Dataset → Cloudflare Worker /news.csv → BarReplay`

## Workflowها

### 1) Download and publish date range
از تب **Actions** اجرا می‌شود. ورودی‌های `start_date` و `end_date` با قالب `YYYY-MM-DD` می‌گیرد، ماه‌های لازم را فقط یک‌بار دریافت می‌کند، بازه دقیق را فیلتر و در Hugging Face منتشر می‌کند.

### 2) Publish previous day news
هر شب ساعت **00:20 UTC** اجرا می‌شود (`20 0 * * *`) و روز قبل را دریافت می‌کند. علاوه بر فایل روزانه، `news.csv` تجمیعی را بدون رکورد تکراری به‌روزرسانی می‌کند.

## تنظیم GitHub

1. یک Hugging Face **Dataset** بسازید.
2. در GitHub → Settings → Secrets and variables → Actions:
   - Secret: `HF_TOKEN` با دسترسی Write
   - Variable: `HF_REPO_ID` مثل `username/barreplay-news`
3. پروژه را Push کنید و Workflow دستی را برای یک بازه کوتاه آزمایش کنید.

## اجرای محلی

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
python -m barreplay_news scrape --start 2026-09-01 --end 2026-09-22 --output dist/range.csv
HF_TOKEN=... HF_REPO_ID=user/dataset python -m barreplay_news publish --input dist/range.csv --start 2026-09-01 --end 2026-09-22
```

## Cloudflare Worker

فایل `worker/src/news-route.js` را در Worker فعلی BarReplay وارد کنید و شاخه `/news.csv` را **قبل از Router موجود** قرار دهید. اگر Worker را مستقل Deploy می‌کنید، `wrangler.toml.example` را به `wrangler.toml` کپی کنید.

متغیر Worker:
- `HF_REPO_ID`
- `HF_REVISION=main`
- در Dataset خصوصی، Secret اختیاری `HF_TOKEN`

پس از Deploy:

```text
https://YOUR-WORKER.workers.dev/news.csv
```

اکسپرت BarReplay 10.16 به بالا، وقتی `InpNewsUrl` خالی باشد، خودکار از `<InpDlBaseUrl>/news.csv` استفاده می‌کند. برای Worker جداگانه، URL بالا را در `InpNewsUrl` قرار دهید و دامنه Worker را در MT5 → Tools → Options → Expert Advisors → Allow WebRequest اضافه کنید. راهنمای کامل اتصال در `expert/README.md` قرار دارد.

## نکته پایداری

Forex Factory ممکن است ساختار HTML یا سیاست ضدربات خود را تغییر دهد و IPهای GitHub Actions را محدود کند. پروژه Retry، Timeout و تأخیر بین ماه‌ها دارد؛ با این حال شکست Workflow باید از تب Actions بررسی شود. شرایط استفاده منبع را رعایت کنید.
