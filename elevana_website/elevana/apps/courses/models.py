from django.db import models
from django.utils.text import slugify

CURRENCY_CHOICES = [
    ('USD', 'USD ($)'),
    ('KES', 'KES (KSh)'),
    ('EUR', 'EUR (€)'),
    ('GBP', 'GBP (£)'),
]

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
    PRICING_CHOICES = [
        ('module', 'Per Module'),
        ('semester', 'Per Semester'),
        ('term', 'Per Term'),
    ]
    pricing_type = models.CharField(max_length=10, choices=PRICING_CHOICES, default='module')
    base_price_kes = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(
        max_length=3, 
        choices=CURRENCY_CHOICES, 
        default='USD'
    )
    image = models.ImageField(upload_to='courses/')
    
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)