from __future__ import unicode_literals
import io
import json

from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.utils.translation import ugettext_lazy as _

from rest_framework.parsers import JSONParser

from src.bucket import Bucket, push_file_task


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user




class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)


    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Device(models.Model):
    mac = models.CharField(max_length=20)
    model = models.CharField(max_length=20)



class MessageLevelManager(models.Manager):
    # Though unnecessary, just wrote it to save the uniformity of
    #   the code. TODO replace this with a code with better approach
    def get_export_to_cloud_task_sig(self, overwrite=True):
        # pylint: disable-msg=import-outside-toplevel
        from .serializers import MessageLevelSerializer

        bucket = Bucket()
        queryset = MessageLevel.objects.all()



class MessageLevel(models.Model):
    title = models.CharField(max_length=10, unique=True, primary_key=True)

    objects = MessageLevelManager()

    def __str__(self):
        return self.title


class MessageManager(models.Manager):
    def get_export_to_cloud_task_sig(self, overwrite=True):
        # pylint: disable-msg=import-outside-toplevel

        from .serializers import MessageSerializer

        queryset = Message.objects.all()



class Message(models.Model):
    code = models.CharField(max_length=50, unique=True)


    objects = MessageManager()

    def __str__(self):
        return "[" + str(self.level) + "]: " + self.code[4:].replace("_", " ")


class KeyManager(models.Manager):
    def import_keys(self):
        # pylint: disable-msg=import-outside-toplevel
        from .serializers import KeySerializer

        Key.objects.all().delete()



class Key(models.Model):
    filename = models.CharField(max_length=50, primary_key=True)
    last_modified = models.DateTimeField()

    objects = KeyManager()

    def __str__(self):
        return self.filename
