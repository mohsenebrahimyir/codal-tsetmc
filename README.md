# کدال و بورس در پایتون

این پکیچ برای ذخیره داده‌های سایت کدال و بازار سرمایه برای اهداف تحلیل بنیادی تهیه شده است.

آموزش پکیج:
    - <https//mohsenebrahimyir.github.io/codal-tsetmc/>

## پایگاه داده

### TSETMC

- [X] `tehran_stocks`: ویرایش بعضی از کدهای بسته

- [X] `stock_capital`: پایگاه داده افزایش سرمایه

### CODAL

- [X] `companies`: لیست تمام شرکت‌ها
- [X] `company_statuses`: وضعیت شرکت‌ها
- [X] `company_types`: نوع شرکت‌ها
- [X] `report_types`: گروه اطلاعیه‌ها
- [X] `financial_years`: سال مالی‌ها
- [X] `letter_types`: نوع گزارش
- [X] `auditors`: حسابرس‌ها

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

## نصب پکیج

نصب از `pypi`:

```python
pip install -U codal-tsetmc
```

نصب از `github`

```python
pip install git+https://github.com/mohsenebrahimyir/codal-tsetmc.git
```

## گرفتن اطلاعات مستقیم

گرفتن تاریخچه قیمت شاخص

```python
from codal_tsetmc.download.tsetmc.price import get_index_prices_history

get_index_prices_history()
```
```
	date	price	code	ticker
0	13870914000000	9248.9	32097828799138957	INDEX
1	13870915000000	9248.9	32097828799138957	INDEX
2	13870916000000	9178.3	32097828799138957	INDEX
3	13870917000000	9130.5	32097828799138957	INDEX
4	13870918000000	9089.2	32097828799138957	INDEX
...	...	...	...	...
3480	14020220000000	2277713.1	32097828799138957	INDEX
3481	14020223000000	2214024.3	32097828799138957	INDEX
3482	14020224000000	2285904.0	32097828799138957	INDEX
3483	14020225000000	2301380.1	32097828799138957	INDEX
3484	14020227000000	2321336.1	32097828799138957	INDEX
```


### گرفتن تایخچه قیمت سهم

```python
symbol = "فولاد"
code = "46348559193224090"
```

```python
from codal_tsetmc.download.tsetmc.price import get_stock_prices_history

get_stock_prices_history(code)
```
```
	date	ticker	price	code
0	13851220000000	FOLD	1900.0	46348559193224090
1	13851221000000	FOLD	1938.0	46348559193224090
2	13851222000000	FOLD	1973.0	46348559193224090
3	13851223000000	FOLD	1934.0	46348559193224090
4	13851226000000	FOLD	1898.0	46348559193224090
...	...	...	...	...
3562	14020219000000	FOLD	6580.0	46348559193224090
3563	14020220000000	FOLD	6560.0	46348559193224090
3564	14020223000000	FOLD	6420.0	46348559193224090
3565	14020224000000	FOLD	6670.0	46348559193224090
3566	14020225000000	FOLD	6680.0	46348559193224090
```


### گرفتن تاریخچه افزایش سرمایه

```python
from codal_tsetmc.download.tsetmc.capital import get_stock_capitals_history

get_stock_capitals_history(code)
```
```
date	new	old	code
8	13891125000000	2.580000e+10	1.580000e+10	46348559193224090
7	13920505000000	3.600000e+10	2.580000e+10	46348559193224090
6	13930515000000	5.000000e+10	3.600000e+10	46348559193224090
5	13940726000000	7.500000e+10	5.000000e+10	46348559193224090
4	13971130000000	1.300000e+11	7.500000e+10	46348559193224090
3	13981022000000	2.090000e+11	1.300000e+11	46348559193224090
2	14000303000000	2.930000e+11	2.090000e+11	46348559193224090
1	14010518000000	5.300000e+11	2.930000e+11	46348559193224090
0	14011228000000	8.000000e+11	5.300000e+11	46348559193224090
```


## ساختن دیتابیس


ایجاد دیتابیس

```python
from codal_tsetmc import init_db

init_db()
```

**اگر در محیط ژوپیتر استفاده می‌کنید این کد را اجرا کنید.**

```python
import nest_asyncio; nest_asyncio.apply()
```

پر کردن تمام پایگاه داده (این کار زمان بر است اما برای اولین بار پیشنهاد می‌شود)


```python
from codal_tsetmc import fill_db

fill_db()
```

## گرفتن لینک با تنظیم فیلتر برای جستجوی گزارشات از کدال


دانلود داده‌های مورد نیاز برای جستجو

```python
from codal_tsetmc import fill_categories_table

fill_categories_table()
```

پر کردن جدول شرکت‌های لیست شده در کدال

```python
from codal_tsetmc import fill_companies_table

fill_companies_table()
```

### تعریف یک جستجو


1. تنظیم فیلترهای دلخواه


```python
from codal_tsetmc import CodalQuery
 
query = CodalQuery()
```

2. نام نماد

```python
query.set_symbol("فولاد")
```

3.  از تاریخ

```python
query.set_from_date("1400/01/01")
```

4. گروه اطلاعیه

```python
query.set_category('اطلاعات و صورت مالی سالانه')
```

5. نوع اطلاعیه

```python
query.set_letter_type('اطلاعات و صورتهای مالی میاندوره ای')
```

6. حذف حسابرسی نشده‌ها

```python
query.set_not_audited(False)
```

7. فقط زیر مجموعه‌ها

```python
query.set_childs(False)
```

8. گرفتن لینک برای مرورگر

```python
query.get_report_list_url()
```

9. گرفتن لینک برای api

```python
query.get_query_url()
```

10. گرفتن لیست گزارشات 

```python
query.get_api_multi_page()
```

## ذخیره داده‌های `tsetmc`

پر کردن جدوال اطلاعات سهام‌ها

```python
from codal_tsetmc import fill_stocks_table

fill_stocks_table()
```

پر کردن جدول قیمت شرکت‌ها


```python
from codal_tsetmc import fill_stocks_prices_table

fill_stocks_prices_table()
```

پر کردن جدول افزایش سرمایه‌ها

```python
from codal_tsetmc import fill_stocks_capitals_table

fill_stocks_capitals_table()
```

## ذخیره داده‌های کامودیتی از سایت‌هایی مثل `tgju`


```python
from codal_tsetmc import fill_commodities_prices_table

fill_commodities_prices_table()
```

## اطلاعات یک سهم

ساختن یک شی از سهام

```python
from codal_tsetmc import Stocks

stock = Stocks.query.filter_by(symbol="فولاد").first()
stock
```
```
فولاد-فولاد مباركه اصفهان-فلزات اساسي
```

مشاهده مشخصات سهم

```python
print(f"""
symbol: {stock.symbol}
name: {stock.name}
isin: {stock.isin}
code: {stock.code}
capital: {stock.capital}
""")
```
```
symbol: فولاد
name: فولاد مباركه اصفهان
isin: IRO1FOLD0009
code: 46348559193224090
capital: 800000000000
```


گرفتن اطلاعات تاریخی سهم

```python
stock.df
```
```
	jdate	ticker	symbol	code	price	capital	index	dollar	market
date									
2008-12-06	13870916	FOLD	فولاد	46348559193224090	2199.0	1.580000e+10	9.178300e+12	3.392988e+09	3.474420e+13
2008-12-07	13870917	FOLD	فولاد	46348559193224090	2134.0	1.580000e+10	9.130500e+12	3.289483e+09	3.371720e+13
2008-12-08	13870918	FOLD	فولاد	46348559193224090	2070.0	1.580000e+10	9.089200e+12	3.197067e+09	3.270600e+13
2008-12-10	13870920	FOLD	فولاد	46348559193224090	2008.0	1.580000e+10	9.023700e+12	3.122677e+09	3.172640e+13
2008-12-13	13870923	FOLD	فولاد	46348559193224090	1948.0	1.580000e+10	8.973300e+12	3.056445e+09	3.077840e+13
...	...	...	...	...	...	...	...	...	...
2023-05-09	14020219	FOLD	فولاد	46348559193224090	6580.0	8.000000e+11	2.305838e+15	9.897714e+09	5.264000e+15
2023-05-10	14020220	FOLD	فولاد	46348559193224090	6560.0	8.000000e+11	2.277713e+15	9.911050e+09	5.248000e+15
2023-05-13	14020223	FOLD	فولاد	46348559193224090	6420.0	8.000000e+11	2.214024e+15	9.699534e+09	5.136000e+15
2023-05-14	14020224	FOLD	فولاد	46348559193224090	6670.0	8.000000e+11	2.285904e+15	1.007724e+10	5.336000e+15
2023-05-15	14020225	FOLD	فولاد	46348559193224090	6680.0	8.000000e+11	2.301380e+15	1.009235e+10	5.344000e+15
```