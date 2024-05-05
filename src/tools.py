import redis
from datetime import datetime, timezone

from django.http import JsonResponse
from django.conf import settings

from celery import group
from celery.result import GroupResult

from src.celery import app
from src.bucket import Bucket

# TODO Maybe better modularization?


def admin_export_json(model):
    try:
        sig = model.objects.get_export_to_cloud_task_sig()
    except Exception as e:
        sig = async_exception.signature((str(e),), immutable=True)

    if not settings.SYNC_FLAG:
        sig = [sig]
        g_res = group(sig).apply_async(queue="D_lopri_Q")
        g_res.save()
        # Choronometer for task evaluation
        cache = redis.Redis()
        key = str(g_res.id) + "_timestart"
        if not cache.exists(key):
            cache.set(
                key, datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f %z")
            )
        data = {"group_id": g_res.id, "should_update_version": 1, "sync": 0}
        return data
    g_res = sig.apply(throw=True)
    data = {"group_id": None, "should_update_version": 1, "sync": 1}
    return data


def admin_download_logo(queryset):
    # TODO this method can become async (?)
    sig_list = []
    for q in queryset:
        try:
            sig = q.get_download_logo_task_sig()
        except Exception as e:
            sig = async_exception.signature((str(e),), immutable=True)
        sig_list.append(sig)

    g_res = group(sig_list).apply_async(queue="D_lopri_Q")
    g_res.save()
    # Choronometer for task evaluation
    cache = redis.Redis()
    key = str(g_res.id) + "_timestart"
    if not cache.exists(key):
        cache.set(key, datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f %z"))
    data = {"group_id": g_res.id, "should_update_version": 0, "sync": 0}
    return data


def admin_upload_logo(queryset):
    sig_list = []
    for q in queryset:
        try:
            sig = q.get_upload_logo_task_sig()
        except Exception as e:
            sig = async_exception.signature((str(e),), immutable=True)
        sig_list.append(sig)

    g_res = group(sig_list).apply_async(queue="D_lopri_Q")
    g_res.save()
    # Choronometer for task evaluation
    cache = redis.Redis()
    key = str(g_res.id) + "_timestart"
    if not cache.exists(key):
        cache.set(key, datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f %z"))
    data = {"group_id": g_res.id, "should_update_version": 0, "sync": 0}
    return data


def admin_download_map(queryset):
    sig_list = []
    for q in queryset:
        try:
            sig = q.get_download_map_task_sig()
        except Exception as e:
            sig = async_exception.signature((str(e),), immutable=True)
        sig_list.append(sig)

    g_res = group(sig_list).apply_async(queue="D_lopri_Q")
    g_res.save()
    # Choronometer for task evaluation
    cache = redis.Redis()
    key = str(g_res.id) + "_timestart"
    if not cache.exists(key):
        cache.set(key, datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f %z"))
    data = {"group_id": g_res.id, "should_update_version": 0, "sync": 0}
    return data


def admin_upload_map(queryset):
    pass

    


@app.task(name="tools.async_exception")
def async_exception(exception_str):
    raise RuntimeError(exception_str)
