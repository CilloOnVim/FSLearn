# learning/forms.py
from django import forms

from .models import Section, Theme, Word


class WordForm(forms.ModelForm):
    class Meta:
        model = Word
        # We don't include 'slug' or 'order' because we want those auto-handled
        fields = ["section", "name", "video", "image", "description"]

        # This adds Bootstrap classes to the input fields so they don't look ugly
        widgets = {
            "section": forms.Select(attrs={"class": "form-select"}),
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. MASAYA"}
            ),
            "video": forms.FileInput(attrs={"class": "form-control"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class ThemeForm(forms.ModelForm):
    class Meta:
        model = Theme
        fields = ["title", "description", "icon", "order"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. Science & Nature"}
            ),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "icon": forms.FileInput(attrs={"class": "form-control"}),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
        }


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ["theme", "title", "order"]
        widgets = {
            "theme": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. Solar System"}
            ),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
        }
