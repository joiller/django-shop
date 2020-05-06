from django.urls import path
from django.contrib import admin
from .views import *

urlpatterns=[
    # path('admin/',admin.site.urls),
    path('',homepage),
    path('products/',products),
    path('getaccounts/',accounts),
    path('login/',login),
    path('purchase',purchase),
    path('helper/',helper),
    path('charge/',charge),
    path('extract/',extract)
]