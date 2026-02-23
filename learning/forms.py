# learning/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Section, Theme, Word, QuizQuestion, QuizChoice, Story


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


class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ["theme", "title", "video", "thumbnail", "description"]
        widgets = {
            "theme": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Ang Kwento ni Pagong"}),
            "video": forms.FileInput(attrs={"class": "form-control"}),
            "thumbnail": forms.FileInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Short summary of the story..."}),
        }


class QuizQuestionForm(forms.ModelForm):
    class Meta:
        model = QuizQuestion
        fields = ['text', 'video']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'What happens next?'}),
            'video': forms.FileInput(attrs={'class': 'form-control'}),
        }

class QuizChoiceForm(forms.ModelForm):
    class Meta:
        model = QuizChoice
        fields = ['text', 'image', 'is_correct']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Answer text'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# This is the magic element. It ties Choices directly to a Question.
# extra=4 gives the teacher 4 blank answer slots by default.
ChoiceFormSet = inlineformset_factory(
    QuizQuestion, QuizChoice, form=QuizChoiceForm,
    extra=4, can_delete=True
)
