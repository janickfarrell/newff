# اتصال BarReplay به خبرها

## حالت پیشنهادی: همان Worker فعلی

Route فایل `worker/src/news-route.js` را پیش از Router فعلی Worker قرار دهید تا مسیر زیر فعال شود، بدون اینکه مسیرهای دیتای بازار تغییر کنند:

```text
https://eurusd.artinmahdavi.workers.dev/news.csv
```

در BarReplay 10.16 و بالاتر، اگر `InpNewsUrl` خالی باشد، اکسپرت به‌صورت خودکار آدرس `<InpDlBaseUrl>/news.csv` را استفاده می‌کند. بنابراین اگر `InpDlBaseUrl` همان Worker بالا است، تغییر دیگری در کد اکسپرت لازم نیست.

## حالت جایگزین: Worker مستقل خبر

Worker پوشه `worker/` را جداگانه Deploy و مقدار زیر را در تنظیمات اکسپرت قرار دهید:

```text
InpNewsUrl=https://YOUR-NEWS-WORKER.workers.dev/news.csv
```

## تنظیم MT5

دامنه Worker را در مسیر زیر به فهرست مجاز اضافه کنید:

`Tools → Options → Expert Advisors → Allow WebRequest for listed URL`

فایل دانلودشده توسط BarReplay در مسیر اشتراکی خبر ذخیره می‌شود:

```text
Common\Files\BarReplay\Shared\News\news.csv
```

> Worker نمونه نباید بدون ادغام Router جایگزین Worker فعلی بازار شود؛ نسخه مستقل برای مسیرهای غیر از `/news.csv` پاسخ 404 می‌دهد.
