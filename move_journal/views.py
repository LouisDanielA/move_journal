import os
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views import View


import requests
from .models import *
from .forms import *

from django.views.generic.base import TemplateView
from django.views.generic import ListView, CreateView
from datetime import datetime, timedelta, date

import re
from django.urls import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Q
import pandas as pd
import json
from .helpers import report_po0
import redis
from django.core.cache import cache
from move_journal.calculate import get_value, set_cache

 


# Для расчетов
class CalculationView(View):
    def get(self, request, *args, **kwargs):
        up=self.request.GET.get('date')
        name = self.request.GET.get('name')
        time = datetime.strptime(up, '%d.%m.%Y').date()
        # print('time str ', time)
        # print('type time ', type(time))
        # print('все ключи ', cache.keys('*'))
        # cache.delete(f'Расчет в пробе слив 25/Металл/Золото/в тв./н-2022-09-01 00:00:00')

        # ---------------------------------
        result = set_cache(name, time)
        #--------------------------------------
        # cache.clear(prefix="1")
        
        # result = get_value(name, time)
        # return HttpResponse(result)
        return JsonResponse(result, safe=False)
    


# Форма с значениями
JournalFormSet = forms.modelformset_factory(Value, fields=('quide', 'up', 'value'), form=ValueForm)


# получить словарь со справочником, для дерева в шаблоне
def get_tree(parent=None, level=0):
    guide = Quide.objects.filter(ancestor=parent)
    if guide:
        d = {}
        spaces = ""     
        for i in range(0,level):
            spaces+="  "
        for obj in guide:
            d[f'{obj.name}'] = get_tree(obj.id, level+1)
    else:
        d= {}
    return d


# Просмотр и добавление              
class MoveIntView(TemplateView):
    """Cоздание данных и просмотр модели Журнал движения и сырья"""
    template_name = "oo/move_zhournal/move_journal.html"

    # def get(self, *args, **kwargs):
    #     thun = Quide.objects.filter(formula__contains='ЕСЛИ')
    #     print(' глянем ', thun)
    #     return super().get(*args, **kwargs)

    # def get(self, *args, **kwargs):
    #     formset = JournalFormSet(queryset=Value.objects.none())
    #     all_data = Value.objects.all().order_by('-id')[:3]
    #     guide = Quide.objects.all()
    #     print('all_data', all_data)
    #     return self.render_to_response({'formset': formset, 'all_data': all_data, 'guide': guide})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = JournalFormSet(queryset=Value.objects.none())
        context['form'] = QuideForm()
        context['all_data'] = Value.objects.all().order_by('-id')[:3]
        context['guide'] = get_tree()
        context['menu'] = Quide.objects.filter(Q(ancestor=None))
        operations = ['-', '+', '/', '*', '(', ')', 'reset']
        context['operations'] = operations

        tags = []
        for t in Quide.objects.filter(Q(ancestor=None)):
            tags.append(t.get_object())
        # print('tags without autocomplite', tags)
        context['tags'] = tags
        return context
        
    def post(self, request, *args, **kwargs):
        formset = JournalFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            return redirect(reverse_lazy("move_view"))
        else:
            print('какая то ошибка видимо', formset.errors)
        return self.render_to_response({'formset': formset})
		
  
# Добавление справочника  
class PostQuide(View):
    def post(self, request, *args, **kwargs):
        form = QuideForm(request.POST)
        print('request.POST', request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, f'Наименование: {request.POST.get("name")}. \n Формула: {request.POST.get("formula")}')
            return redirect('move_view')
        else:
            print('какая то ошибка видимо form ', form.errors)
            
            return render(request, 'oo/move_zhournal/modal_error.html', context={'form': form})
    
    
  
  
# Для автозаполнения полей с данными
class AutoComplete(MoveIntView):
    def get(self, request, *args, **kwargs): 
        if self.request.is_ajax():
            name_group = request.GET.get('indicator')
            response_data = {}

            tags = []
            for t in Quide.objects.filter(Q(ancestor__name=name_group)):
                tags.append(t.get_object())
            # print('forcheck', tags)
            response_data['name_group'] = tags            
                
            return HttpResponse(json.dumps(response_data), content_type="application/json")


# Просмотр
class MoveListView(ListView):
    model = Value
    template_name = "oo/move_zhournal/move_list.html"
    form_class = ValueForm

    def get_queryset(self):
        start_time = datetime(datetime.now().year, datetime.now().month, 1)
        if start_time.month != 12:
            end_time = datetime(datetime.now().year,
                                datetime.now().month+1, 1)-timedelta(seconds=1)
        else:
            end_time = datetime(datetime.now().year+1, 1,
                                1)-timedelta(seconds=1)
        queryset = Value.objects.filter(up__range=(start_time, end_time)).order_by('up')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_time = datetime(datetime.now().year, datetime.now().month, 1)
        end_time = datetime(datetime.now().year,
                            datetime.now().month+1, 1)-timedelta(seconds=1)
        context['start'] = str(start_time)
        context['stop'] = str(end_time)
        return context

    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)


# Фильтры
class MoveFilterListView(MoveListView):
    """Фильтры для модели"""

    def get_queryset(self):
        start_time = datetime.strptime(
            self.request.GET['start'] + '-01 00:00:00', '%Y-%m-%d %H:%M:%S')
        if self.request.GET.get('stop') != None:
            end_time = datetime.strptime(
                self.request.GET['stop'] + '-01 00:00:00', '%Y-%m-%d %H:%M:%S')
            if end_time.month != 12:
                end_time_clean = datetime(
                    end_time.year, end_time.month+1, 1)-timedelta(seconds=1)
            else:
                end_time_clean = datetime(
                    end_time.year+1, 1, 1)-timedelta(seconds=1)
            queryset = Value.objects.filter(up__range=(
                start_time, end_time_clean)).order_by('up')
        else:
            if start_time.month != 12:
                end_time_clean = datetime(
                    start_time.year, start_time.month+1, 1)-timedelta(seconds=1)
            else:
                end_time_clean = datetime(
                    start_time.year+1, 1, 1)-timedelta(seconds=1)
            queryset = Value.objects.filter(
                up__range=(start_time, end_time_clean)).order_by('up')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.GET.get('stop') != None:
            context['start'] = self.request.GET['start']
            context['stop'] = self.request.GET['stop']
            context['check_checkbox'] = ''
            context['change_dateinput'] = ''
        else:
            context['start'] = self.request.GET['start']
            context['check_checkbox'] = 'checked'
            context['change_dateinput'] = 'disabled'
        return context

    def get(self, *args, **kwargs):
        export_data = self.request.GET.get('export_data', False)
        if export_data:
            if self.request.GET.get('stop'):
                r = report_po0(self.request.GET.get('start'),
                               self.request.GET.get('stop'))
            else:
                r = report_po0(self.request.GET.get('start'))
            file_path = r.build()

            #Индикатор того что мой контент будет отработан браузером как вложенный файл
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    response = HttpResponse(f.read(
                    ), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    response['Content-Disposition'] = 'attachment; filename=' + \
                        os.path.basename(file_path)
                    return response
            raise Http404

        return super().get(*args, **kwargs)


# Просмотр
class MoveQuideList(ListView):
    model = Quide
    template_name = "oo/move_zhournal/move_quide.html"
    # form_class = QuideForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = QuideForm()
        return context

    # def get(self, *args, **kwargs):
    #     return super().get(*args, **kwargs)


# # Фильтры
# class MoveFilterListView(MoveListView):
#     """Фильтры для модели"""

#     def get_queryset(self):
#         start_time = datetime.strptime(
#             self.request.GET['start'] + '-01 00:00:00', '%Y-%m-%d %H:%M:%S')
#         if self.request.GET.get('stop') != None:
#             end_time = datetime.strptime(
#                 self.request.GET['stop'] + '-01 00:00:00', '%Y-%m-%d %H:%M:%S')
#             if end_time.month != 12:
#                 end_time_clean = datetime(
#                     end_time.year, end_time.month+1, 1)-timedelta(seconds=1)
#             else:
#                 end_time_clean = datetime(
#                     end_time.year+1, 1, 1)-timedelta(seconds=1)
#             queryset = Value.objects.filter(up__range=(
#                 start_time, end_time_clean)).order_by('up')
#         else:
#             if start_time.month != 12:
#                 end_time_clean = datetime(
#                     start_time.year, start_time.month+1, 1)-timedelta(seconds=1)
#             else:
#                 end_time_clean = datetime(
#                     start_time.year+1, 1, 1)-timedelta(seconds=1)
#             queryset = Value.objects.filter(
#                 up__range=(start_time, end_time_clean)).order_by('up')
#         return queryset

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         if self.request.GET.get('stop') != None:
#             context['start'] = self.request.GET['start']
#             context['stop'] = self.request.GET['stop']
#             context['check_checkbox'] = ''
#             context['change_dateinput'] = ''
#         else:
#             context['start'] = self.request.GET['start']
#             context['check_checkbox'] = 'checked'
#             context['change_dateinput'] = 'disabled'
#         return context

#     def get(self, *args, **kwargs):
#         export_data = self.request.GET.get('export_data', False)
#         if export_data:
#             if self.request.GET.get('stop'):
#                 r = report_po0(self.request.GET.get('start'),
#                                self.request.GET.get('stop'))
#             else:
#                 r = report_po0(self.request.GET.get('start'))
#             file_path = r.build()

#             #Индикатор того что мой контент будет отработан браузером как вложенный файл
#             if os.path.exists(file_path):
#                 with open(file_path, 'rb') as f:
#                     response = HttpResponse(f.read(
#                     ), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#                     response['Content-Disposition'] = 'attachment; filename=' + \
#                         os.path.basename(file_path)
#                     return response
#             raise Http404

#         return super().get(*args, **kwargs)
