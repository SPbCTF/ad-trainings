from django import forms
from models import CatRecord


class AddRecordForm (forms.ModelForm):
    class Meta:
        model = CatRecord