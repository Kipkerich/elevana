import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                                           serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='applications',
                    to='courses.course',
                )),
                # Personal
                ('email', models.EmailField(max_length=254)),
                ('id_number', models.CharField(max_length=100, verbose_name='ID Number')),
                ('date_of_birth', models.DateField()),
                ('gender', models.CharField(
                    max_length=20,
                    choices=[('female', 'Female'), ('male', 'Male'),
                             ('prefer_not', "Don't want to mention")],
                )),
                ('is_person_with_disability', models.CharField(
                    max_length=3,
                    choices=[('yes', 'Yes'), ('no', 'No')],
                    verbose_name='Person with Disability?',
                )),
                ('country', models.CharField(max_length=100)),
                ('religion', models.CharField(
                    max_length=50,
                    choices=[
                        ('christianity', 'Christianity'), ('islam', 'Islam'),
                        ('hinduism', 'Hinduism'), ('buddhism', 'Buddhism'),
                        ('other', 'Other'), ('prefer_not', 'Prefer Not to Say'),
                    ],
                )),
                # Contact
                ('first_mobile_number', models.CharField(max_length=20)),
                ('second_mobile_number', models.CharField(max_length=20, blank=True)),
                # Education
                ('highest_education_level', models.CharField(
                    max_length=50,
                    choices=[
                        ('primary', 'Primary'),
                        ('secondary', 'Secondary / High School'),
                        ('certificate', 'Certificate'),
                        ('diploma', 'Diploma'),
                        ('bachelors', "Bachelor's Degree"),
                        ('masters', "Master's Degree"),
                        ('phd', 'PhD / Doctorate'),
                        ('other', 'Other'),
                    ],
                )),
                ('year_of_completion', models.CharField(max_length=4)),
                ('mean_grade', models.CharField(
                    max_length=20, verbose_name='Mean Grade / Final Grade')),
                # Next of kin
                ('next_of_kin_name', models.CharField(max_length=200)),
                ('next_of_kin_mobile', models.CharField(
                    max_length=50, verbose_name='Next of Kin Mobile Numbers')),
                # Location
                ('home_county', models.CharField(max_length=100)),
                ('country_outside_kenya', models.CharField(max_length=100, blank=True)),
                ('current_residence_town', models.CharField(
                    max_length=100, verbose_name='Current Residence / Town')),
                # Payment
                ('payment_reference', models.CharField(max_length=100, unique=True, blank=True)),
                ('payment_status', models.CharField(
                    max_length=20,
                    choices=[('unpaid', 'Unpaid'), ('paid', 'Paid'), ('failed', 'Failed')],
                    default='unpaid',
                )),
                # Consent
                ('data_consent', models.CharField(
                    max_length=3,
                    choices=[('yes', 'Yes'), ('no', 'No')],
                    verbose_name='Data Protection Consent',
                )),
                # Status / meta
                ('status', models.CharField(
                    max_length=20,
                    choices=[
                        ('draft', 'Draft'), ('pending', 'Pending'),
                        ('reviewed', 'Reviewed'), ('accepted', 'Accepted'),
                        ('rejected', 'Rejected'),
                    ],
                    default='draft',
                )),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['-submitted_at']},
        ),
    ]
