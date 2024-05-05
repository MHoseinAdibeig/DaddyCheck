import json
from django.db import models
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    MinLengthValidator,
)
from django.conf import settings




class DeviceModelManager(models.Manager):
    # Though unnecessary, just wrote it to save the uniformity of
    #   the code. TODO replace this with a code with better approach
    def get_export_to_cloud_task_sig(self, overwrite=True):
        # pylint: disable-msg=import-outside-toplevel
        from .serializers import DeviceModelSerializer

        queryset = DeviceModel.objects.all()
        serializer = DeviceModelSerializer(queryset, many=True)
        with open(settings.CDN_LOCAL_DIR + "devicemodels.json", "w") as f:
            json.dump(serializer.data, f)

        return push_file_task.signature(
            ("devicemodels.json", overwrite), immutable=True
        )


class DeviceModel(models.Model):
    id = models.IntegerField(primary_key=True,)
    name = models.CharField(max_length=50, unique=True, blank=False,)
    zoom_level = models.DecimalField(max_digits=2, decimal_places=1, default=1.0)

    objects = DeviceModelManager()

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.name


# TODO Integrate Gadget Info with Gadget model in analysis
class GadgetInfo(models.Model):
    serial_number = models.CharField(max_length=200, unique=True,)
    max_count = models.IntegerField(
        default=4, validators=[MaxValueValidator(99), MinValueValidator(1)], blank=False
    )
    expiration_date = models.CharField(
        max_length=10, validators=[MinLengthValidator(10)], blank=False
    )
    model = models.ForeignKey(DeviceModel, on_delete=models.CASCADE, blank=False)
    imgpath = models.CharField(max_length=200)
    randbits = models.CharField(max_length=100)

    def __str__(self):
        return (
            str(self.id)
            + ": "
            + self.model.name
            + " -- "
            + str(self.expiration_date)
            + " -- "
            + str(self.max_count)
        )
