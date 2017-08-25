class Field(object):
    validators = []

    def __init__(self, default=None):
        self.default = default

    def valid(self, value):
        return all([v(value) for v in self.validators])

    def modify(self, value):
        return None


class IntField(Field):
    validators = [str.isdecimal, ]

    def __init__(self, default=0):
        super().__init__(default)

    def modify(self, value: str):
        return int(value)