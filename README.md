# کدال و بورس در پایتون

این پکیچ برای ذخیره داده‌های سایت کدال و بازار سرمایه برای اهداف تحلیل بنیادی تهیه شده است.

## پایگاه داده

### TSETMC

- [X] `tehran_stocks`: ویرایش بعضی از کدهای بسته
    - 

- [X] `stock_capital`: پایگاه داده افزایش سرمایه

### CODAL

- [X] `companies`: لیست تمام شرکت‌ها
- [X] `company_statuses`: وضعیت شرکت‌ها
- [X] `company_types`: نوع شرکت‌ها
- [X] `report_types`: گروه اطلاعیه‌ها
- [X] `financial_years`:
- [X] `letter_types`:
- [X] `auditors`:

#### OTHER

- [X] `commodities`: افزون قیمت‌های کامودیتی
    - [X] <api.tgju.org>

### Update package

اگر این متن را میبینید یعنی این پکیج درحال توسعه است و قابلیت استفاده در پروژه‌های مهم را ندارد.

```
# python3 -m pip install --upgrade build
python3 -m build

# python3 -m pip install --upgrade twine
python3 -m twine upload --repository pypi dist/*

```
