from django import forms

class ContactForm(forms.Form):
    INQUIRY_CHOICES = [
        ('', 'Select Inquiry Type'),
        ('course', 'Course Information'),
        ('partnership', 'Partnership'),
        ('corporate', 'Corporate Training'),
        ('general', 'General Inquiry'),
    ]

    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}))
    inquiry_type = forms.ChoiceField(choices=INQUIRY_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your Message', 'rows': 6}))