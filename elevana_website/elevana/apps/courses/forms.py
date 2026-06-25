from django import forms
from .models import Course, CourseApplication

# Kenyan counties list
KENYA_COUNTIES = [
    ('', '— Select County —'),
    ('Baringo', 'Baringo'), ('Bomet', 'Bomet'), ('Bungoma', 'Bungoma'),
    ('Busia', 'Busia'), ('Elgeyo-Marakwet', 'Elgeyo-Marakwet'), ('Embu', 'Embu'),
    ('Garissa', 'Garissa'), ('Homa Bay', 'Homa Bay'), ('Isiolo', 'Isiolo'),
    ('Kajiado', 'Kajiado'), ('Kakamega', 'Kakamega'), ('Kericho', 'Kericho'),
    ('Kiambu', 'Kiambu'), ('Kilifi', 'Kilifi'), ('Kirinyaga', 'Kirinyaga'),
    ('Kisii', 'Kisii'), ('Kisumu', 'Kisumu'), ('Kitui', 'Kitui'),
    ('Kwale', 'Kwale'), ('Laikipia', 'Laikipia'), ('Lamu', 'Lamu'),
    ('Machakos', 'Machakos'), ('Makueni', 'Makueni'), ('Mandera', 'Mandera'),
    ('Marsabit', 'Marsabit'), ('Meru', 'Meru'), ('Migori', 'Migori'),
    ('Mombasa', 'Mombasa'), ("Murang'a", "Murang'a"), ('Nairobi', 'Nairobi'),
    ('Nakuru', 'Nakuru'), ('Nandi', 'Nandi'), ('Narok', 'Narok'),
    ('Nyamira', 'Nyamira'), ('Nyandarua', 'Nyandarua'), ('Nyeri', 'Nyeri'),
    ('Samburu', 'Samburu'), ('Siaya', 'Siaya'), ('Taita-Taveta', 'Taita-Taveta'),
    ('Tana River', 'Tana River'), ('Tharaka-Nithi', 'Tharaka-Nithi'),
    ('Trans Nzoia', 'Trans Nzoia'), ('Turkana', 'Turkana'),
    ('Uasin Gishu', 'Uasin Gishu'), ('Vihiga', 'Vihiga'), ('Wajir', 'Wajir'),
    ('West Pokot', 'West Pokot'),
]

YEAR_CHOICES = [('', '— Select Year —')] + [
    (str(y), str(y)) for y in range(2026, 1979, -1)
]


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'department', 'description', 'price', 'image']


class CourseApplicationForm(forms.ModelForm):

    home_county = forms.ChoiceField(
        choices=KENYA_COUNTIES,
        required=True,
        label='Home County',
    )
    year_of_completion = forms.ChoiceField(
        choices=YEAR_CHOICES,
        required=True,
        label='Year of Completion',
    )

    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course', None)
        super().__init__(*args, **kwargs)
        if course:
            self.fields['course'].initial = course
            self.fields['course'].widget = forms.HiddenInput()

        # Apply Bootstrap form-control to all visible fields
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.HiddenInput, forms.RadioSelect)):
                widget = field.widget
                css = widget.attrs.get('class', '')
                if 'form-control' not in css and 'form-select' not in css:
                    if isinstance(widget, forms.Select):
                        widget.attrs['class'] = 'form-select'
                    else:
                        widget.attrs['class'] = 'form-control'

    def clean_data_consent(self):
        value = self.cleaned_data.get('data_consent')
        if value != 'yes':
            raise forms.ValidationError(
                'You must consent to data processing to submit this application.'
            )
        return value

    def clean_year_of_completion(self):
        value = self.cleaned_data.get('year_of_completion')
        if not value:
            raise forms.ValidationError('Please select a year of completion.')
        return value

    def clean_home_county(self):
        value = self.cleaned_data.get('home_county')
        if not value:
            raise forms.ValidationError('Please select your home county.')
        return value

    class Meta:
        model = CourseApplication
        exclude = ['status', 'submitted_at', 'payment_reference', 'payment_status']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'gender': forms.RadioSelect(),
            'is_person_with_disability': forms.RadioSelect(),
            'religion': forms.Select(),
            'highest_education_level': forms.Select(),
            'data_consent': forms.RadioSelect(),
        }