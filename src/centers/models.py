import os
import glob
import json
import requests

from src.bucket import Bucket, push_file_task, pull_file_task
from src.celery import app

from django.db import models
from django.utils.translation import ugettext_lazy as _


class City(models.Model):
    title = models.CharField(max_length=50, primary_key=True)

    class Meta:
        verbose_name_plural = _("cities")

    def __str__(self):
        return self.title


class CategoryManager(models.Manager):
    def get_export_to_cloud_task_sig(self, overwrite=True):
        # Imports are made in-code due to circular import
        # pylint: disable-msg=import-outside-toplevel
        from .serializers import CategorySerializer

        bucket = Bucket()
        queryset = Category.objects.all()
        serializer = CategorySerializer(queryset, many=True)
        with open(bucket.local_dir + "categories.json", "w") as f:
            json.dump(serializer.data, f)

        return push_file_task.signature(("categories.json", overwrite), immutable=True)


class Category(models.Model):
    short_name = models.CharField(max_length=20, primary_key=True)
    title = models.CharField(max_length=50, unique=True)
    logo_image = models.CharField(max_length=100, null=True, blank=True,)
    description = models.CharField(max_length=100, null=True, blank=True)

    objects = CategoryManager()

    class Meta:
        verbose_name_plural = _("categories")

    def __str__(self):
        return self.title

    def get_download_logo_task_sig(self, overwrite=False):
        bucket = Bucket()
        if self.short_name is None:
            raise RuntimeError("Category has no short names")
        res = bucket.search_file(
            "img/categories/logo/" + self.short_name + "(.jpg|.png|.jpeg)"
        )
        if res == []:
            raise RuntimeError("Can't find the file in the bucket")
        path = res[0]
        self.logo_image = path.replace("img/categories/logo", "")
        self.save()
        os.makedirs(bucket.local_dir + "img/categories/logo", exist_ok=True)
        return pull_file_task.signature((path, overwrite), immutable=True)

    def get_upload_logo_task_sig(self, overwrite=False):
        bucket = Bucket()
        if self.short_name is None:
            raise RuntimeError("Category has no short names")
        if self.logo_image is None or not os.path.exists(
            bucket.local_dir + "img/categories/logo/" + self.logo_image
        ):
            filepath = glob.glob(
                bucket.local_dir + "img/categories/logo/{}.*".format(self.short_name)
            )
            if filepath == []:
                raise RuntimeError("Can't find the file to upload: " + self.short_name)
            path = filepath[0].replace(bucket.local_dir, "")
            self.map_image = path.replace("img/categories/logo/", "")
            self.save()
        else:
            path = "img/categories/logo/" + self.logo_image
        return push_file_task.signature((path, overwrite), immutable=True)


class CenterManager(models.Manager):
    def get_export_to_cloud_task_sig(self, overwrite=True):
        # Imports are made in-code due to circular import
        # pylint: disable-msg=import-outside-toplevel
        from .serializers import CenterSerializer

        bucket = Bucket()
        queryset = Center.objects.all()
        serializer = CenterSerializer(queryset, many=True)
        with open(bucket.local_dir + "centers.json", "w") as f:
            json.dump(serializer.data, f)

        return push_file_task.signature(("centers.json", overwrite), immutable=True)


class Center(models.Model):
    title = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=15, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    short_name = models.CharField(max_length=20, null=True, blank=True)
    loc_latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    loc_longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    email = models.EmailField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)
    active_times = models.CharField(max_length=200, null=True, blank=True)
    map_image = models.CharField(max_length=100, null=True, blank=True,)
    logo_image = models.CharField(max_length=100, null=True, blank=True,)

    objects = CenterManager()

    def __str__(self):
        return self.title

    def get_download_logo_task_sig(self, overwrite=False):
        bucket = Bucket()
        if self.short_name is None:
            raise RuntimeError("Center has no short names")
        res = bucket.search_file(
            "img/centers/logo/" + self.short_name + "(.jpg|.png|.jpeg)"
        )
        if res == []:
            raise RuntimeError("Can't find the file in the bucket")
        path = res[0]
        self.logo_image = path.replace("img/centers/logo", "")
        self.save()
        os.makedirs(bucket.local_dir + "img/centers/logo", exist_ok=True)
        return pull_file_task.signature((path, overwrite), immutable=True)

    def get_upload_logo_task_sig(self, overwrite=False):
        bucket = Bucket()
        if self.short_name is None:
            raise RuntimeError("Center has no short names")
        if self.logo_image is None or not os.path.exists(
            bucket.local_dir + "img/centers/logo/" + self.logo_image
        ):
            filepath = glob.glob(
                bucket.local_dir + "img/centers/logo/{}.*".format(self.short_name)
            )
            if filepath == []:
                raise RuntimeError("Can't find the file to upload: " + self.short_name)
            path = filepath[0].replace(bucket.local_dir, "")
            self.map_image = path.replace("img/centers/logo/", "")
            self.save()
        else:
            path = "img/centers/logo/" + self.logo_image
        return push_file_task.signature((path, overwrite), immutable=True)

    def get_download_map_task_sig(self, overwrite=False):
        bucket = Bucket()
        if self.short_name is None:
            raise RuntimeError("Center has no short names")
        if self.loc_latitude is None or self.loc_longitude is None:
            raise RuntimeError("Location is not defined for this center")
        # NOTE Could replace search_file with file_exists, cause map is always .png
        res = bucket.search_file(
            "img/centers/map/" + self.short_name + "(.jpg|.png|.jpeg)"
        )
        os.makedirs(
            bucket.local_dir + "img/centers/map", exist_ok=True
        )  # Map will always get fetched successfully
        if res:
            path = res[0]
            self.logo_image = path.replace("img/centers/map/", "")
            self.save()
            return pull_file_task.signature((path, overwrite), immutable=True)
        path = bucket.local_dir + "img/centers/map/" + self.short_name + ".png"
        return request_map_png.signature((self.pk, path, overwrite), immutable=True,)

    def get_upload_map_task_sig(self, overwrite=False):  # TODO Use *args instead
        bucket = Bucket()
        if self.short_name is None:
            raise RuntimeError("Center has no short names")
        if self.map_image is None or not os.path.exists(
            bucket.local_dir + "img/centers/map/" + self.map_image
        ):
            # NOTE Could replace glob with os.path.exists, cause map is always .png
            filepath = glob.glob(
                bucket.local_dir + "img/centers/map/{}.*".format(self.short_name)
            )
            if filepath == []:
                raise RuntimeError("Can't find the file to upload")
            path = filepath[0].replace(bucket.local_dir, "")
            self.map_image = path.replace("img/centers/map/", "")
            self.save()
        else:
            path = "img/centers/map/" + self.map_image
        return push_file_task.signature((path, overwrite), immutable=True)


@app.task(bind=True, name="centers.request_map_png")
def request_map_png(self, center_pk, path, overwrite=False):
    center = Center.objects.get(pk=center_pk)
    if not overwrite and os.path.exists(path):
        raise RuntimeError(
            "File already exists locally and overwrite argument is False"
        )
    r = requests.get(
        "https://open.mapquestapi.com/staticmap/v4/getmap?key=8hwFJRIGVYSX4t3sjP4FzSiwKBGAhRit&size=1200,800&type=map&imagetype=png&pois=.,"
        + str(center.latitude)
        + ","
        + str(center.longitude)
    )
    with open(path, "wb") as f:
        f.write(r.content)
    center.map_image = center.short_name + ".png"
    center.save()
