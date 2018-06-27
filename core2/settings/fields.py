import re


class Field(object):
    validators = []

    def __init__(self, default=None, validators=None):
        self.default = default
        self.own_validators = validators or []

    def valid(self, value):
        validators = self.validators + self.own_validators
        return all([v(value) for v in validators])

    def modify(self, value):
        return None


class IntField(Field):
    validators = [str.isdecimal, ]

    def __init__(self, default=0, validators=None):
        super().__init__(default, validators)

    def modify(self, value: str):
        return int(value)


class FloatFiled(Field):
    validators = [lambda x: re.match(r'^\d+(\.\d+)?$', x) is not None, ]

    def __init__(self, default=0.0, validators=None):
        super().__init__(default, validators)

    def modify(self, value: str):
        return float(value)


class CharField(Field):
    validators = []

    def __init__(self, default='', validators=None):
        super().__init__(default, validators)

    def modify(self, value: str):
        return value
