from django.db import models
from django.utils.text import slugify


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
        ('male', 'Male'),
        ('female', 'Female'),
        ('non_binary', 'Non-Binary'),
        ('other', 'Other'),
        ('prefer_not', 'Prefer Not to Say'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    # --- Course ---
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='applications')

    # --- Personal Details ---
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    nationality = models.CharField(max_length=100)
    id_passport_number = models.CharField(max_length=100)

    # --- Contact Information ---
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    permanent_address = models.TextField()
    mailing_address = models.TextField(blank=True, help_text='Leave blank if same as permanent address')
    emergency_contact_name = models.CharField(max_length=200)
    emergency_contact_relationship = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=20)

    # --- Academic History ---
    previous_institutions = models.TextField(help_text='List schools/universities attended, one per line')
    graduation_dates = models.TextField(help_text='Month and year of graduation for each institution')
    grades_gpa = models.CharField(max_length=100, blank=True, help_text='Cumulative GPA or grade')
    standardized_test_scores = models.CharField(max_length=200, blank=True, help_text='SAT, ACT, TOEFL, IELTS, etc.')

    # --- Supporting Documents ---
    academic_transcript = models.FileField(upload_to='applications/transcripts/', blank=True, null=True)
    id_photo = models.ImageField(upload_to='applications/photos/', blank=True, null=True, help_text='Passport-sized headshot')
    id_scan = models.FileField(upload_to='applications/id_scans/', blank=True, null=True, help_text='Scan of national ID, birth certificate, or passport')
    personal_statement = models.TextField(help_text='Explain your motivation for applying to this course')
    recommendation_letter = models.FileField(upload_to='applications/recommendations/', blank=True, null=True)

    # --- Background & Interests (Optional) ---
    extracurricular_activities = models.TextField(blank=True, help_text='Clubs, sports, volunteer work, etc.')
    accomplishments = models.TextField(blank=True, help_text='Awards, scholarships, or special certifications')
    special_accommodations = models.TextField(blank=True, help_text='Dietary, medical, or physical accessibility needs')

    # --- Meta ---
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} — {self.course.title}"