# Migration for CourseApplication model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('middle_name', models.CharField(blank=True, max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('date_of_birth', models.DateField()),
                ('gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('non_binary', 'Non-Binary'), ('other', 'Other'), ('prefer_not', 'Prefer Not to Say')], max_length=20)),
                ('nationality', models.CharField(max_length=100)),
                ('id_passport_number', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone_number', models.CharField(max_length=20)),
                ('permanent_address', models.TextField()),
                ('mailing_address', models.TextField(blank=True, help_text='Leave blank if same as permanent address')),
                ('emergency_contact_name', models.CharField(max_length=200)),
                ('emergency_contact_relationship', models.CharField(max_length=100)),
                ('emergency_contact_phone', models.CharField(max_length=20)),
                ('previous_institutions', models.TextField(help_text='List schools/universities attended, one per line')),
                ('graduation_dates', models.TextField(help_text='Month and year of graduation for each institution')),
                ('grades_gpa', models.CharField(blank=True, help_text='Cumulative GPA or grade', max_length=100)),
                ('standardized_test_scores', models.CharField(blank=True, help_text='SAT, ACT, TOEFL, IELTS, etc.', max_length=200)),
                ('academic_transcript', models.FileField(blank=True, null=True, upload_to='applications/transcripts/')),
                ('id_photo', models.ImageField(blank=True, help_text='Passport-sized headshot', null=True, upload_to='applications/photos/')),
                ('id_scan', models.FileField(blank=True, help_text='Scan of national ID, birth certificate, or passport', null=True, upload_to='applications/id_scans/')),
                ('personal_statement', models.TextField(help_text='Explain your motivation for applying to this course')),
                ('recommendation_letter', models.FileField(blank=True, null=True, upload_to='applications/recommendations/')),
                ('extracurricular_activities', models.TextField(blank=True, help_text='Clubs, sports, volunteer work, etc.')),
                ('accomplishments', models.TextField(blank=True, help_text='Awards, scholarships, or special certifications')),
                ('special_accommodations', models.TextField(blank=True, help_text='Dietary, medical, or physical accessibility needs')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('reviewed', 'Reviewed'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='courses.course')),
            ],
            options={
                'ordering': ['-submitted_at'],
            },
        ),
    ]
