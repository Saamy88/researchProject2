#!/usr/local/bin/python
from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^about/$', views.about, name='about'),
    url(r'^upload/$', views.upload, name='upload'),
    url(r'^skos/$', views.skos, name='skos'),
    url(r'^corpus/$', views.corpus, name='corpus'),
    url(r'^corpus_fetch/$', views.corpus_fetch, name='corpus_fetch'),

]
