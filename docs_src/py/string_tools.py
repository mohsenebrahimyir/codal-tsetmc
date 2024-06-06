def digit_en_to_fa(string: str) -> str:
    fa = "۰۱۲۳۴۵۶۷۸۹"
    for i in range(len(string)):
        if string[i] in "0123456789":
            string = string.replace(string[i], fa[int(string[i])])

    return string