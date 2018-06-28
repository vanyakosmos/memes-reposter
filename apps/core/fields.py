from django import forms
from django.core import validators
from django.db import models


class URLField(models.TextField):
    default_validators = [validators.URLValidator()]

    def formfield(self, **kwargs):
        defaults = {
            'form_class': forms.URLField,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)
