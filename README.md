# کدال و بورس در پایتون

این پکیچ برای ذخیره داده‌های سایت کدال و بازار سرمایه برای اهداف تحلیل بنیادی تهیه شده است.

- [آموزش بسته](https://mohsenebrahimyir.github.io/codal-tsetmc/)
- [تلگرام @codal_tsetmc_package](https://t.me/codal_tsetmc_package)


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

## نصب پکیج

نسخه‌های مجاز پایتون از ۳.۱۰ بالاتر باید باشد.

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
