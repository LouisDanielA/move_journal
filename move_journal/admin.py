from django import forms
from django.contrib import admin
from .models import *
from datetime import date, datetime

# Register your models here.
class QuideAdmin(admin.ModelAdmin):
    # list_filter = ('name', )
    search_fields = ['name']
    class Media:
        js = ("copy_name.js",)
    
    
admin.site.register(Quide, QuideAdmin)


class ValueAdminForm(forms.ModelForm):
    search_fields = ['quide__name']
    class Meta:
        model = Value
        fields = ('quide', 'up', 'value')
    def clean(self):
        cleaned_data = super().clean()
        up = cleaned_data.get('up')
        current_date = date.today()
        valid_date = current_date - up
        print('valid_date', valid_date.days)
        # if valid_date.days>30:
        #     raise forms.ValidationError("Не допустимо изменять значения сроком более месяца")
        return cleaned_data
    
class ValueAdmin(admin.ModelAdmin):
    form = ValueAdminForm


admin.site.register(Value, ValueAdmin)
# admin.site.register(Value)




