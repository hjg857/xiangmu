from django import forms
from django.conf import settings
from django.contrib import admin
from apps.accounts.models import User
from .models import Region

class RegionAdminForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['region_admin'].queryset = User.objects.filter(role='region_admin')

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    form = RegionAdminForm
    list_display = ('province', 'city', 'name', 'code', 'region_admin', 'is_active')
    list_filter = ('province', 'city', 'is_active')
    search_fields = ('name', 'code', 'province', 'city')
