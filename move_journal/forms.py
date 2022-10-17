
from django.forms import DateField, ModelForm, Form, ValidationError
# from django.core.exceptions import ValidationError
# from django_jsonforms.forms import JSONSchemaField
from .models import *
from django import forms
# from bootstrap_modal_forms.forms import BSModalForm
from datetime import date
import re
from django.apps import apps

class ValueForm(forms.ModelForm):
    class Meta:
        model = Value
        fields = ('quide', 'up', 'value')
        
        widgets = {
            'quide': forms.Select(attrs={
                'class': 'form-control form-control-sm',
                # 'class': 'form-control select2bs4 select2-purple select2-hidden-accessible',
                # 'data-dropdown-css-class': "select2-purple",
                # 'style': "width: 100%;",
                # # 'data-select2-id': "12",
                # 'tabindex': "-1",
                # 'aria-hidden': "true",
                'required': True,
                'onchange': '',
            }),

            'up': forms.DateInput(attrs={
                'class': 'form-control datetimepicker-input form-control-sm',
                'required': True,
                'type': 'date',
                # 'pattern': '[0-9]{4}-[0-9]{2}'
            }),

            'value': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'step': '0.0001',
                'min': '0',
                'value': '',
                'required': True,
            }),
        }
    
    def clean(self):
        # cleaned_data = super().clean()
        quide = self.cleaned_data.get('quide')
        up = self.cleaned_data.get('up')
       
        try:
            obj = Value.objects.get(Q(quide=quide) & Q(up=up))
            print('obj exist', obj)
            raise ValidationError(f'Запись "{quide}" на дату — "{up}" уже существует')
        except ObjectDoesNotExist:
            return self.cleaned_data


class QuideForm(forms.ModelForm):
    class Meta:
        model = Quide
        fields = ('ancestor', 'name', 'formula')
        
        widgets = {
            'ancestor': forms.Select(attrs={
                'class': 'form-control select2 select2-purple select2-hidden-accessible',
                'data-dropdown-css-class': "select2-purple",
                'style': "width: 100%;",
                # 'data-select2-id': "12",
                'tabindex': "-1",
                'aria-hidden': "true",
                'required': True,
                'onchange':'',
            }),
            
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'value': '',
                'required': True,
            }),

            'formula': forms.Textarea(attrs={
                'class': 'form-control form-control-sm',
                'value': '',
                # 'required': True,
                'rows':'2',
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        formula = cleaned_data.get('formula')
        try:
            list_var = re.findall(r"\!(.+?)\!", formula)
            print('list_var', list_var)
            if len(list_var)>0:
                for v in range(len(list_var)):
                    formula = re.sub(rf'!{list_var[v]}!', '1', formula)
            print('formula', formula)
            result = eval(formula)
            print('result', type(result))
            return cleaned_data

        except Exception as e:
            raise ValidationError(f'Введенная формула {formula} не соответствует требуемому формату!')
        

# class QuideModelForm(BSModalForm):
#     class Meta:
#         model = Quide
#         fields = ['ancestor', 'name', 'formula']









