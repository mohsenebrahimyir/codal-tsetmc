# کدال و بورس در پایتون

این پکیچ برای ذخیره داده‌های سایت کدال و بازار سرمایه برای اهداف تحلیل بنیادی تهیه شده است.

- [آموزش بسته](https://mohsenebrahimyir.github.io/codal-tsetmc/)
- [تلگرام @codal_tsetmc_package](https://t.me/codal_tsetmc_package)
- [ایتا @codal_tsetmc_package](https://eitaa.com/codal_tsetmc_package)

## هشدار

اگر این متن را میبینید یعنی این پکیج درحال توسعه است و قابلیت استفاده در پروژه‌های مهم را ندارد.

```bash
# python3 -m pip install --upgrade build
python3 -m build
```

```bash
# python3 -m pip install --upgrade twine
python3 -m twine upload --repository pypi dist/*
```

## پایگاه داده

### TSETMC

- [X] `tehran_stocks`: الهام از بسته
- [X] `stock`: لیست تمام سهام‌ها و صندوق‌ها و ...
- [X] `stock_capital`: پایگاه داده افزایش سرمایه
  - باید دقت کنیم که بعضی از افزایش سرمایه‌‌های سایت tsetmc بروز نیست و باید برای محاسبه مقدار دقیق از صورت‌های مالی شرکت‌ها استفاده کرد.
- [X] `stock_price`: قیمت و حجم معاملات روزانه
- [X] `stock_group`:

### CODAL

- [X] `company`: لیست تمام شرکت‌ها
- [X] `company_state`: وضعیت شرکت‌ها
- [X] `company_type`: نوع شرکت‌ها
- [X] `report_type`: گروه اطلاعیه‌ها
- [X] `letter_type`: نوع گزارش
- [X] `auditor`: حسابرس‌ها
- [X] `financial_year`: سال مالی‌ها
- [X] `letter`: گزارشات مالی

## نصب پکیج

برای استفاده از این بسته پیشنهاد می‌شود از محیط مجازی استفاده کنید.

```bash
python -m venv .venv
```

فعال سازی محیط مجازی در لینوکس

```bash
source .venv/bin/activate
```

فعال سازی محیط مجازی در ویندوز

```cmd
> .\venv\Scripts\activate
```

نصب از `pypi`:

```bash
pip install -U codal-tsetmc
```

نصب از نسخه در حال توسعه `github`

```bash
pip install git+https://github.com/mohsenebrahimyir/codal-tsetmc.git
```
