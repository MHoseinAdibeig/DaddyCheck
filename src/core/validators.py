import re

from .models import User
from src.exceptions import MessagedException
from src.gadget_master.models import DeviceModel


def is_valid_password(password):
    if len(password) < 8:
        raise MessagedException(message="err_password_tooshort")

    return True


def is_valid_devicemodel(devicemodel):
    if not DeviceModel.objects.filter(name=devicemodel).exists():
        print("device model: \'", devicemodel, "\'")
        raise MessagedException(message="err_device_incompatible")


