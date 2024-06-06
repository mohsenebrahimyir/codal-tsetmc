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
- [X] `stocks`: لیست تمام سهام‌ها و صندوق‌ها و ...
- [X] `stock_capital`: پایگاه داده افزایش سرمایه
  - باید دقت کنیم که بعضی از افزایش سرمایه‌‌های سایت tsetmc بروز نیست و باید برای محاسبه مقدار دقیق از صورت‌های مالی شرکت‌ها استفاده کرد.
- [X] `stock_price`: قیمت و حجم معاملات روزانه

### CODAL

- [X] `companies`: لیست تمام شرکت‌ها
- [X] `company_statuses`: وضعیت شرکت‌ها
- [X] `company_types`: نوع شرکت‌ها
- [X] `report_types`: گروه اطلاعیه‌ها
- [X] `letter_types`: نوع گزارش
- [X] `auditors`: حسابرس‌ها
- [X] `financial_years`: سال مالی‌ها
- [X] `letter`: گزارشات مالی
- [X] `financial_statement_header`: سربرگ صورت‌های مالی
- [X] `financial_statement_table_with_single_item`: جدول‌های صورت‌های مالی با مقادیر ساده (یعنی فقط یک مقدار برای هر گزینه در هر سال دارند)
  - [X] Staff status: وضعیت کارکنان
  - [X] Balance Sheet: صورت وضعيت مالي
  - [X] Other operating income: سایر درآمدهای عملیاتی
  - [X] Other operating expenses: سایر هزینه‌های عملیاتی
  - [X] Non-operation income and expenses investment income: سایر درآمدها و هزینه‌های غیرعملیاتی - درآمد سرمایه‌گذاری‌ها
  - [X] Non-operation income and expenses miscellaneous items: سایر درآمدها و هزینه‌های غیرعملیاتی - اقلام متفرقه
  - [X] Income Statement: صورت سود و زيان
  - [X] Cash Flow: صورت جريان‌هاي نقدي
  - [X] Sales trend and cost over the last 5 years: روند فروش و بهای تمام شده در 5 سال اخیر
  - [X] The cost of the sold goods: بهای تمام شده
  - [X] Balance Sheet: صورت وضعیت مالی
  - [X] Income Statement: صورت سود و زیان
  - [X] Cash Flow: صورت جریان‌های نقدی
  - [X] Balance Sheet: ترازنامه
  - [X] Cash Flow: جریان وجوه نقد

#### OTHER

- [X] `commodities_price`: افزون قیمت‌های کامودیتی
  - [X] price_dollar_rl: قیمت دلار آژاد به صورت پیش فرض

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
