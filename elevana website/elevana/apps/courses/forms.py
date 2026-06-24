from django import forms
from .models import Course, CourseApplication


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'department', 'description', 'price', 'image']


class CourseApplicationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        # Allow pre-selecting the course from the detail page
        course = kwargs.pop('course', None)
        super().__init__(*args, **kwargs)
        if course:
            self.fields['course'].initial = course
            self.fields['course'].widget = forms.HiddenInput()

        # Add Bootstrap form-control class to every visible field
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.HiddenInput):
                field.widget.attrs.setdefault('class', 'form-control')

    class Meta:
        model = CourseApplication
        exclude = ['status', 'submitted_at']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'permanent_address': forms.Textarea(attrs={'rows': 3}),
            'mailing_address': forms.Textarea(attrs={'rows': 3}),
            'previous_institutions': forms.Textarea(attrs={'rows': 4}),
            'graduation_dates': forms.Textarea(attrs={'rows': 3}),
            'personal_statement': forms.Textarea(attrs={'rows': 6}),
            'extracurricular_activities': forms.Textarea(attrs={'rows': 3}),
            'accomplishments': forms.Textarea(attrs={'rows': 3}),
            'special_accommodations': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'id_passport_number': 'National ID / Passport Number',
            'id_photo': 'Identification Photo (passport-sized)',
            'id_scan': 'Identification Scan (ID, birth cert, or passport)',
        }