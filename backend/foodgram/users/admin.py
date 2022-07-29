from django.contrib import admin

from .models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    """Class to customize users display in admin panel."""

    list_display = [
        'pk', 'username', 'email', 'first_name', 'last_name',
        'is_staff', 'date_joined']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    list_filter = ['username', 'email', 'is_staff', 'date_joined']
    empty_value_display = '-empty-'


class SubscriptionAdmin(admin.ModelAdmin):
    """Class to customize subscriptions display in admin panel."""

    list_display = ['pk', 'user', 'author']
    search_fields = ['user', 'author']


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
