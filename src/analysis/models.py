import os
import glob
import shlex
import json
import uuid
import subprocess

from celery import chord

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from src.core.models import Device, User, Message
from src.bucket import Bucket, push_file_task


class StateManager(models.Manager):
    # Though unnecessary, just wrote it to save the uniformity of
    #   the code. TODO replace this with a code with better approach
    def get_export_to_cloud_task_sig(self, overwrite=True):
        # pylint: disable-msg=import-outside-toplevel
        from .serializers import StateSerializer

        bucket = Bucket()
        queryset = State.objects.all()
        serializer = StateSerializer(queryset, many=True)
        with open(bucket.local_dir + "states.json", "w") as f:
            json.dump(serializer.data, f)

        return push_file_task.signature(("states.json", overwrite), immutable=True)


class State(models.Model):
    code = models.CharField(max_length=20, primary_key=True)
    message = models.ForeignKey(
        Message, on_delete=models.SET_NULL, to_field="code", null=True, blank=True
    )



class Gadget(models.Model):
    serial_number = models.CharField(max_length=200, unique=True)
    register_date = models.DateTimeField(auto_now_add=True)


class Analysis(models.Model):
    # UUID field is chosen because analysis_id is used in API
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50, null=True, blank=True)


    class Meta:
        verbose_name_plural = _("analyses")

    def __str__(self):
        return self.title or str(self.id)

    def upload_files(self):
       pass

    def analyse(self):
        # pylint: disable=too-many-locals
        # pylint: disable=import-outside-toplevel
        pass


class SampleDetail(models.Model):
    analysis = models.OneToOneField(
        Analysis,
        on_delete=models.CASCADE,
    )
    viscosity = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    volume = models.CharField(max_length=50)

    def __str__(self):
        return f"For {self.analysis}"


class Result(models.Model):
    analysis = models.ForeignKey(
        Analysis,
        on_delete=models.CASCADE,
    )


    class Meta:
        unique_together = [["analysis", "iteration"]]

    def __str__(self):
        if self.iteration == 0:
            return f"Final result for {self.analysis}"
        return f"Result #{self.iteration} for {self.analysis}"
