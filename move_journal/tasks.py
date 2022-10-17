from apscheduler.schedulers.background import BackgroundScheduler
from .models import *
from datetime import date

from django.conf import settings
from django.core.mail import send_mail


def check_data():
    all_tags = []
    for t in Quide.objects.filter(Q(ancestor=None)):
        all_tags.append(t.get_object())
    tags_with_value = []
    
    def get_name_with_value(tags):
        for tag in tags:
            if len(tag['children'])>0:
                get_name_with_value(tag['children'])
            else:
                tags_with_value.append(tag['name'])
                
    get_name_with_value(all_tags)
    print('tags_with_value',len(tags_with_value))
    
    current_values = Value.objects.filter(Q(up=date.today()))
    print('current_values', len(current_values))
    
    if len(current_values) == len(tags_with_value):
        pass
    else:
        print('Здесь нужно отправлять сообщение на почту, мол не все данные введены')
        subject = 'Добрый день, начальник!'
        message = 'Не заполнены, некоторые поля за вчерашний день!'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = ['MizanbaevAE@polymetal.kz', ]
        send_mail(subject, message, email_from, recipient_list)
    

def start():
    scheduler = BackgroundScheduler()
    # scheduler.add_job(check_data, 'cron', month='1-12', day_of_week ='0-6', hour='12', minute='14', second='00', id='send_email', max_instances=1)
    scheduler.add_job(check_data, 'interval', seconds=15)
    scheduler.start()