from django.db import models
from django.utils.text import slugify
import uuid


class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='courses/')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class CourseApplication(models.Model):
    GENDER_CHOICES = [
        ('female', 'Female'),
        ('male', 'Male'),
        ('prefer_not', "Don't want to mention"),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]
    EDUCATION_LEVEL_CHOICES = [
        ('primary', 'Primary'),
        ('secondary', 'Secondary / High School'),
        ('certificate', 'Certificate'),
        ('diploma', 'Diploma'),
        ('bachelors', "Bachelor's Degree"),
        ('masters', "Master's Degree"),
        ('phd', 'PhD / Doctorate'),
        ('other', 'Other'),
    ]
    RELIGION_CHOICES = [
        ('christianity', 'Christianity'),
        ('islam', 'Islam'),
        ('hinduism', 'Hinduism'),
        ('buddhism', 'Buddhism'),
        ('other', 'Other'),
        ('prefer_not', 'Prefer Not to Say'),
    ]
    DISABILITY_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]
    DATA_CONSENT_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]

    # --- Course ---
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='applications')

    # --- Personal Details ---
    email = models.EmailField()
    id_number = models.CharField(max_length=100, verbose_name='ID Number')
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    is_person_with_disability = models.CharField(
        max_length=3, choices=DISABILITY_CHOICES,
        verbose_name='Person with Disability?'
    )
    country = models.CharField(max_length=100)
    religion = models.CharField(max_length=50, choices=RELIGION_CHOICES)

    # --- Contact ---
    first_mobile_number = models.CharField(max_length=20)
    second_mobile_number = models.CharField(max_length=20, blank=True)

    # --- Education ---
    highest_education_level = models.CharField(max_length=50, choices=EDUCATION_LEVEL_CHOICES)
    year_of_completion = models.CharField(max_length=4, help_text='e.g. 2020')
    mean_grade = models.CharField(max_length=20, verbose_name='Mean Grade / Final Grade',
                                  help_text='e.g. B+ or 3.8/4.0')

    # --- Next of Kin ---
    next_of_kin_name = models.CharField(max_length=200)
    next_of_kin_mobile = models.CharField(max_length=50, verbose_name='Next of Kin Mobile Numbers')

    # --- Location ---
    home_county = models.CharField(max_length=100)
    country_outside_kenya = models.CharField(max_length=100, blank=True,
                                             help_text='Fill only if you reside outside Kenya')
    current_residence_town = models.CharField(max_length=100, verbose_name='Current Residence / Town')

    # --- Payment ---
    payment_reference = models.CharField(max_length=100, unique=True, blank=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')

    # --- Consent ---
    data_consent = models.CharField(
        max_length=3, choices=DATA_CONSENT_CHOICES,
        verbose_name='Data Protection Consent',
        help_text=(
            'By filling this form, you are consenting that the data being given shall be used '
            'solely for purposes of training and deployment for attachment engagement.'
        )
    )

    # --- Meta ---
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.email} — {self.course.title}"

    def save(self, *args, **kwargs):
        if not self.payment_reference:
            self.payment_reference = f"ELEV-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)