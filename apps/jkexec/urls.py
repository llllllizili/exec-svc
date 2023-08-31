#!/usr/bin python
# -*- encoding: utf-8 -*-
'''
@File    :   urls.py
@Time    :   2020/05/29 13:43:42
'''



from . import views
from django.urls import path,include
from rest_framework.routers import DefaultRouter


router = DefaultRouter()

router.register('task_trigger', views.TaskTrigger, basename='task_trigger')
router.register('register_resource', views.RegisterResource, basename='register_resource')
# router.register('host_list', views.HostList, base_name='host_list')

urlpatterns = [
    path('', include(router.urls)),
]