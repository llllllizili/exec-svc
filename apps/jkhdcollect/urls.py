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

router.register('task_trigger', views.jkCollectSync, basename='jkCollectSync')
router.register('model_grepper', views.jkCollectAdaption, basename='jkCollectAdaption')

# router.register('ilo', views.RegisterResource, basename='register_resource')

urlpatterns = [
    path('', include(router.urls)),
]