# -*- coding: utf-8 -*-
import random
import string
from django.db import models
from django.contrib.auth.models import User
from super_secret_crypto import super_secret_hash


class CatUser(User):
    friend_token = models.CharField(max_length=15, verbose_name=u'Токен для друзей')

    def __init__(self, *args, **kwargs):
        super(CatUser, self).__init__(*args, **kwargs)
        self.friend_token = str(super_secret_hash(self.username))


class CatRecord(models.Model):

    image = models.ImageField(verbose_name=u'Изображение', upload_to='cats/')
    owner = models.ForeignKey(CatUser, verbose_name=u'Владелец')
    is_private = models.BooleanField(verbose_name=u'Закрытое изображение', default=False)
    title = models.CharField(max_length=255, verbose_name=u'Заголовок/теги', blank=True)

    class Meta:
        verbose_name = u'Картинка'
        verbose_name_plural = u'Картинки'

    def __unicode__(self):
        return u'%s (%s)' % (self.image.name, self.owner)
