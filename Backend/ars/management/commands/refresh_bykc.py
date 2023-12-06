from django.core.management.base import BaseCommand, CommandError
from ars.models import User
from ars.bykchandler.update_selected import update_unselected
import time
import random


class Command(BaseCommand):
    help = 'Use a random valid sso user in database to refresh all bykc'

    def handle(self, *args, **options):
        active_user = User.objects.all().filter(bykc_isactive=True)
        update_succeed = False
        for user in active_user:
            if update_succeed:
                time.sleep(30 + random.randrange(0, 30))
            try:
                update_unselected(user)
                update_succeed = True
                print('succeed using user ' + user.username + ' ' + user.sso_password)
            except Exception as e:
                update_succeed = False
                print('user ' + user.username + ' failed! error message is ' + e.args[0])
