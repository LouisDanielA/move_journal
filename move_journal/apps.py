from django.apps import AppConfig
import os
from django.conf import settings
from django.core.mail import send_mail
from pathlib import Path


class MoveJournalConfig(AppConfig):
    name = 'move_journal'

    def ready(self):
        from move_journal import tasks
        # if os.environ.get('RUN_MAIN'):
        # tasks.start()
        subject = 'Добрый день, начальник!'
        message = 'Не заполнены, некоторые поля за вчерашний день!'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = ['', ]
        send_mail(subject, message, email_from, recipient_list)
        
