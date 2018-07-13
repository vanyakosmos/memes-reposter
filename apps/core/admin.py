from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import SiteConfig, Stat


class CountListFilter(admin.SimpleListFilter):
    title = 'Count filter'
    parameter_name = 'count'

    def lookups(self, request, model_admin):
        return (
            ('nonzero', 'Above zero'),
            ('zero', 'Zero'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'zero':
            return queryset.filter(count=0)
        if self.value() == 'nonzero':
            return queryset.filter(count__gt=0)


@admin.register(SiteConfig)
class SiteConfigAdmin(SingletonModelAdmin):
    pass


@admin.register(Stat)
class StatAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'app', 'task', 'count', 'note', 'blank')
    readonly_fields = ('created_at', 'app', 'task', 'count', 'note', 'blank')
    list_filter = ('app', 'task', 'blank', CountListFilter,)
