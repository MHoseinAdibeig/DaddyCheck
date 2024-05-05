from django import forms

from .models import Center


class CenterForm(forms.ModelForm):
    class Meta:
        model = Center
        fields = "__all__"
        widgets = {
            "phone": forms.TextInput(
                attrs={
                    "placeholder": "Ex. 09123456789",
                    "autocomplete": "off",
                    "pattern": "0[0-9]{6,11}",
                    "title": "Enter a valid phone number starting with 0 with length between 7 and 12",
                }
            ),
            "short_name": forms.TextInput(
                attrs={
                    "pattern": "[a-z]*",
                    "title": "Short name must be in lowercase without numbers or space or special characters",
                }
            ),
            "logo_image": forms.TextInput(attrs={"readonly": "on",}),
            "map_image": forms.TextInput(attrs={"readonly": "on",}),
        }
