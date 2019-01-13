from django.contrib import admin

from .models import TelegramChannel


@admin.register(TelegramChannel)
class TelegramChannelAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'subs', 'uuid')
    readonly_fields = ('uuid',)

    def subs(self, channel: TelegramChannel):
        return ', '.join([str(s) for s in channel.subscriptions.all()])
