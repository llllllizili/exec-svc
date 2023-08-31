#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   urls.py
@Time    :   2020/11/12 13:58:14
'''


from . import views
from django.urls import path,include
from rest_framework.routers import DefaultRouter


router = DefaultRouter()

router.register('task_trigger', views.jkK8s, basename='jkk8s')

urlpatterns = [
    path('', include(router.urls)),
]