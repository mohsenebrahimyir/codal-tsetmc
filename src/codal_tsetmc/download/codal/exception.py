import re


class BadValueInput:
    def __init__(self, value):
        self.value = value

    def boolian_type(self):
        if not isinstance(self.value, bool):
            raise TypeError("status must be True or False")

    def integer_type(self):
        if not isinstance(self.value, int):
            raise TypeError("status must be integer")

    def string_type(self):
        if not isinstance(self.value, str):
            raise TypeError("status must be String")

    def int_str_type(self):
        pattern = "^\d*$"
        if not bool(re.match(pattern, self.value)):
            raise TypeError("status must be Integer String")

    def date_type(self):
        pattern = "^\d{4}\/(0?[1-9]|1[012])\/(0?[1-9]|[12][0-9]|3[01])$"
        if not bool(re.match(pattern, self.value)):
            raise TypeError("status must be yyyy/mm/dd")


if __name__ == '__main__':
    pass
