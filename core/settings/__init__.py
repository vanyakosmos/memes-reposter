from core.store import SettingsStore
from .fields import Field


class SettingsError(Exception):
    pass


class Settings(object):
    def __init__(self, store: SettingsStore):
        self.store = store
        self.fields = self.set_up_fields()
        self._settings = {}
        self.refresh()
        self.set_properties()

    def set_properties(self):
        for field_name in self._settings:
            setattr(self.__class__, field_name,
                    property(lambda _, n=field_name: self._settings[n]))

    def set_up_fields(self):
        fs = {}
        for attr in dir(self):
            if attr.startswith("__"):
                continue
            obj = getattr(self, attr, None)
            if isinstance(obj, Field):
                fs[attr] = obj
        return fs

    def set(self, key, value):
        if key not in self.fields:
            raise SettingsError('Unknown setting.')
        field = self.fields[key]
        if field.valid(value):
            self.store.set_setting(key, value)
            self.refresh(key, value)
        else:
            raise SettingsError('Invalid setting value.')

    def items(self):
        return self._settings.items()

    def refresh(self, key=None, value=None):
        if key:
            self._settings[key] = value
            return

        store_items = self.store.get_settings()
        for key, field in self.fields.items():
            value = store_items.get(key, field.default)
            value = field.modify(value)
            self._settings[key] = field.modify(value)
