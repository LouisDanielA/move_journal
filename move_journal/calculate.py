
import pandas as pd
from django.db.models import Sum, Q
import re

from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta, date
from django.core.cache import cache


def set_cache(name, time):
    if cache.get(f'{name}-{time}'):
        res = cache.get(f'{name}-{time}')
        print('данные взяты из кэша ', res)
    else:
        print('not in cache')
        res = get_value(name, time)
        cache.set(f'{name}-{time}', res)
        print('данные добавлены в кэш ', res)
    return res


# Сумма с начала месяца или годаы
def get_sum(name, start, current_time):
    from .models import Quide, Value
    formula = Quide.objects.get(name=name).formula

    if formula != None:
        date_list = pd.date_range(
            start=start, end=current_time).to_pydatetime().tolist()

        result = 0
        for t in date_list:
            result += set_cache(name, t)
            
    else:
        result = Value.objects.filter(quide__name=name, up__range=(
            start, current_time)).aggregate(Sum('value'))['value__sum']
        
    return result


# коллекция методов для формул
case = {'СУММА': get_sum}

# коллекция параметров для формул: пример —>
parameters = {'d': 'days'}
    

def get_result_sum(exp, time, month):
    item = (re.findall(r"\((.+?)\)", exp))[0]
    start = datetime(time.year, month, 1, 0, 0)
    print('функция сработала')
    result = case['СУММА'](item, start, time)
    return result

def get_value(name, time):
    from .models import Quide, Value
    # получаю формулу для ячейки
    try:
        formula = Quide.objects.get(name=name).formula
        # print('formula ssad', formula)

    except ObjectDoesNotExist:
        formula = None

    # print('formula try', formula)

    # если формула есть
    if formula is not None and formula != '':
        # получаю список наименовании полей
        list_var = re.findall(r"\!(.+?)\!", formula)

        # перебираю этот список
        for v in range(len(list_var)):
            if 'СУММА_М' in list_var[v]:
                result = get_result_sum(list_var[v], time, time.month)
                return result
                    
            elif 'СУММА_Г' in list_var[v]:
                result = get_result_sum(list_var[v], time, 1)
                return result
                
            elif "ЕСЛИ" in formula:
                print('почему не падает')
                expressions = re.findall(r"\[(.+?)\]", formula)
                print('expressions ', expressions)
                condition_item = re.findall(r"\!(.+?)\!", expressions[0])
                print('condition_item ', condition_item)
                condition_res = get_value(condition_item, time)
                print('condition_res ', condition_res)
                expressions[0] = re.sub(rf'!{condition_item}!', rf'{condition_res}', expressions[0])
                print('expressions[0] ', expressions[0])
                result = 0
                # if expressions[0]:
                #     cond_v = re.findall(r"\!(.+?)\!", cond_var[1])
                #     print('cond_v ', cond_v)
                #     for n in range(len(cond_v)):
                #         item = set_cache(cond_v[n], time)
                #         formula = re.sub(
                #             rf'!{cond_v[n]}!', rf'{item}', formula)
                        
                # else:
                #     cond_v = re.findall(r"\!(.+?)\!", cond_var[2])
                #     for n in range(len(cond_v)):
                #         item = set_cache(cond_v[n], time)
                #         formula = re.sub(rf'!{cond_v[n]}!', rf'{item}', formula)
                        
                # def set_condition():.
                    
                    
            else:
                # рекурсия
                item = set_cache(list_var[v], time)
                # try:
                #     item = set_cache(list_var[v], time)
                # except ObjectDoesNotExist:
                #     item = 0

                formula = re.sub(rf'!{list_var[v]}!', rf'{item}', formula)

        try:
            result = round(eval(formula), 5)
            print(f'конечная сумма — {name} — ', time, ' ',  result)
        except Exception as e:
            result = 0
        

    else:
        # если формул нету, значит это значение хранится в базе
        # print('должен падать сюда, без формулы', name)
        
            # result = Value.objects.get(quide__name=name, up=time).value
            if cache.get(f'{name}-{time}'):
                result = cache.get(f'{name}-{time}')
                print('данные взяты из кэша ', result)
            else:
                print('not in cache')
                try:
                    result = Value.objects.get(quide__name=name, up=time).value
                except ObjectDoesNotExist:
                    result = 0
                    
                cache.set(f'{name}-{time}', result)
                print('данные добавлены в кэш ', result)
            
            
            print('result_value ', result)
    return result


