# کدال و بورس در پایتون

## پایگاه داده

### TSETMC

- [X] `tehran_stocks`: ویرایش بعضی از کدهای بسته
- [X] `stock_client`: پایگاه داده خرید و فروش حقیقی و حقوقی
- [X] `stock_dividend`: پایگاه داده تقسیم سود.
- [X] `stock_capital`: پایگاه داده افزایش سرمایه
- [X] `stock_adjsuted`: پایگاه داده تعدیل قیمت

### CODAL

- [X] `companies`: لیست تمام شرکت‌ها
- [X] `company_statuses`: وضعیت شرکت‌ها
- [X] `company_types`: نوع شرکت‌ها
- [X] `report_types`: گروه اطلاعیه‌ها
- [X] `financial_years`: 
- [X] `letter_types`:
- [X] `auditors`:


### Update package

```
# python3 -m pip install --upgrade build
python3 -m build

# python3 -m pip install --upgrade twine
python3 -m twine upload --repository pypi dist/*

```
