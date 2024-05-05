from .models import GadgetInfo, DeviceModel
from django import forms


class GadgetForm(forms.ModelForm):
    number_of_all = forms.IntegerField(
        label="Total Count", initial=1, widget=forms.NumberInput(attrs={"min": "1",})
    )

    class Meta:
        model = GadgetInfo
        fields = (
            "model",
            "expiration_date",
            "max_count",
        )
        labels = {
            "model": "Device Model",
            "expiration_date": "Expiration Date",
            "max_count": "Max Usage Count",
        }
        widgets = {
            "expiration_date": forms.TextInput(
                attrs={
                    "placeholder": "Ex. 2020-01-01",
                    "pattern": "(?:19|20)[0-9]{2}-(?:(?:0[1-9]|1[0-2])-(?:0[1-9]|1[0-9]|2[0-9])|(?:(?!02)(?:0[1-9]|1[0-2])-(?:30))|(?:(?:0[13578]|1[02])-31))",
                    "autocomplete": "off",
                }
            ),
        }


def identity():
    if len(DeviceModel.objects.all()) > 0:
        objs = DeviceModel.objects.all()
        ids = map(lambda x: x.id, objs)
        ids = sorted(ids)
        j = 1
        for i in ids:
            if j != i:
                return j
            j = j + 1
        return j
    return 1


class DeviceForm(forms.ModelForm):
    class Meta:
        model = DeviceModel
        fields = (
            "id",
            "name",
            "zoom_level",
        )
        labels = {
            "id": "Device Model ID",
            "name": "Device Model Name",
            "zoom_level": "Device Zoom Level",
        }
        widgets = {
            "id": forms.NumberInput(attrs={"value": identity, "autocomplete": "off",}),
            "name": forms.TextInput(
                attrs={"placeholder": "Ex. Galaxy J7", "autocomplete": "off",}
            ),
        }
