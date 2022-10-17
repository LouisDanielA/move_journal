from django.db import models

from django.conf import settings
from django.db import models
from django.db.models import Q
from datetime import date, datetime
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save

from django.forms import DateField, ModelForm, Form, ValidationError

from django.contrib import messages
from move_journal.calculate import get_value

import redis
from django.core.cache import cache


# Справочник 1
class Quide(models.Model):
    ancestor = models.ForeignKey('self', on_delete=models.CASCADE,
                                 blank=True, null=True, verbose_name="Родитель", related_name='childrens')
    name = models.CharField('Название', max_length=255, null=True, blank=True, default='') # добавить проверку на уникальность
    formula = models.TextField(null=True, blank=True, default='', verbose_name="Формула")
    
    def children(self):
        return Quide.objects.filter(Q(ancestor=self.pk)&Q(formula=None))

    def get_object(self):
        flag = ''
        # проверяю добавлены ли значения за сегодняшний день
        try:
            obj = Value.objects.get(quide__name = self.name, quide__ancestor = self.ancestor, up=date.today())
            data = obj.value
            flag = 'green' 
            # print('green', flag)
        except ObjectDoesNotExist:
            flag = 'red'
            data = None
            # print('red', flag)
        if data!=None:
            obj = {'name': self.name, 'data': data, 'id': self.id, 'flag': flag, 'children': []}
        else:
            obj = {'name': self.name, 'id': self.id, 'flag': flag, 'children': []}
            
        for child in self.children():
            obj['children'].append(child.get_object())
            
        return obj    
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):         
        if self.ancestor and not self.id:
            self.name = self.ancestor.name + '/' + self.name 
        super().save(*args,**kwargs)
        
    class Meta:
        managed = True
        verbose_name = "Справочник"
        verbose_name_plural = "Справочник"
           

# Справочник 2
class Value(models.Model):
    quide = models.ForeignKey(
        'Quide', on_delete=models.CASCADE, verbose_name="Справочное наименование")
    up = models.DateField("Учетный период", default=date.today, null=True, blank=True) 
    value = models.FloatField("Значение", null=True, blank=True) 
    
    def __str__(self):
        return str(self.quide.name)+'/'+str(self.up)+'/'+str(self.value)

    def save(self, *args, **kwargs):
        result = get_value(self.quide.name, self.up)
        cache.set(f'{self.quide.name}-{self.up}', result)
        super().save(*args, **kwargs)

    class Meta:
        managed = True
        verbose_name = "Данные"
        verbose_name_plural = "Данные"
        

# для обновления данных 
def update_redis(sender, instance, created, **kwargs):
    if created:
        print('created_working1')
    else:
        print('changing_working1')
        # print('все ключи ', cache.keys('*'))
        
        print('обновляю значения кэша')
        result = get_value(instance.quide.name, instance.up)
        
        del_data = Quide.objects.filter(Q(formula__icontains=instance.quide.name))

        for obj in del_data:
            cache.delete(f'{obj.name}-{instance.up}')
            
        cache.set(f'{instance.quide.name}-{instance.up}', result)
        
post_save.connect(update_redis, sender=Value)