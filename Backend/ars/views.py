from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from ars.models import *
from ars.serializers import *

from rest_framework.views import APIView
from ars.init_db import init_db

class Init_DB_view(APIView):

    def post(self, request):
        init_db()
