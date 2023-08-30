# کدال و بورس در پایتون

این پکیچ برای ذخیره داده‌های سایت کدال و بازار سرمایه برای اهداف تحلیل بنیادی تهیه شده است.

آموزش پکیج: <https//mohsenebrahimyir.github.io/codal-tsetmc/>

### هشدار

اگر این متن را میبینید یعنی این پکیج درحال توسعه است و قابلیت استفاده در پروژه‌های مهم را ندارد.

```
# python3 -m pip install --upgrade build
python3 -m build

# python3 -m pip install --upgrade twine
python3 -m twine upload --repository pypi dist/*

```

## پایگاه داده

### TSETMC

- [X] `tehran_stocks`: ویرایش بعضی از کدهای بسته

- [X] `stock_capital`: پایگاه داده افزایش سرمایه

### CODAL

- [X] `companies`: لیست تمام شرکت‌ها
- [X] `company_statuses`: وضعیت شرکت‌ها
- [X] `company_types`: نوع شرکت‌ها
- [X] `report_types`: گروه اطلاعیه‌ها
- [X] `letter_types`: نوع گزارش
- [X] `auditors`: حسابرس‌ها
- [ ] `financial_years`: سال مالی‌ها

#### OTHER

- [X] `commodities`: افزون قیمت‌های کامودیتی

## نصب پکیج

برای استفاده از این بسته پیشنهاد می‌شود از محیط مجازی استفاده کنید.

```bash
$ python -m venv .venv
```

فعال سازی محیط مجازی در لینوکس


```bash
$ source .venv/bin/activate
```

```bash
> .\venv\Scripts\activate
```

نصب از `pypi`:

```bash
(.venv) $ pip install -U codal-tsetmc
```

نصب از نسخه در حال توسعه `github`

```bash
(.venv) $ pip install git+https://github.com/mohsenebrahimyir/codal-tsetmc.git
```
