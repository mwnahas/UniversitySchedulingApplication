from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from datetime import time
from django.urls import reverse


# django didn't give me an option to select days of the week for the week without it looking terrible
# so a tuple is created and the integer field is replaced with a field for days of the week


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'), ('instructor', 'Instructor'), ('ta', 'TA'),
    ]
    full_name = models.CharField(max_length=100)
    role      = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return self.full_name

#anyone shouldbe able to see this, (user bio)
class PublicProfile(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, unique=True, related_name='public_profile')
    email = models.EmailField(blank=True)
    office_location = models.CharField(max_length=100, blank=True)
    office_hours = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Public profile of {self.user.username}"

    def get_absolute_url(self):
        return reverse('public-profile', kwargs={'username': self.user.username})
    #private info, the one that only admins and that user can see (private contact info)


class PrivateProfile(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, unique=True, related_name='private_profile')
    home_address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)

    #checking to make sure phone number is digits without importing anything
    def save(self, *args, **kwargs):
        #checks if the phone_number field is empty before checking if it's correct
        if self.phone_number and not self.phone_number.isdigit():
            raise ValueError("Phone number must contain digits only.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Private profile of {self.user.username}"


DAYS_OF_WEEK = [
    ('1', 'Monday'),
    ('2', 'Tuesday'),
    ('3', 'Wednesday'),
    ('4', 'Thursday'),
    ('5', 'Friday'),
    ('6', 'Saturday'),
    ('7', 'Sunday'),
]

class Course(models.Model):
    SEMESTER_CHOICES = [
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('fall', 'Fall'),
        ('winter', 'Winter'),
    ]

    courseName = models.CharField(max_length=100)
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES)
    year = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.courseName} ({self.get_semester_display()} {self.year})"



class Section(models.Model):
    sectionName = models.CharField(max_length=100)
    dayOfWeek = models.CharField(max_length=1, choices=DAYS_OF_WEEK)
    dayOfWeek2 = models.CharField(max_length=1, choices=DAYS_OF_WEEK, blank=True, null=True, default='')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sections", null=True, blank=True)
    teaching_assistant = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="ta_sections", null=True, blank=True)
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="sections_taught", null=True, blank=True)
    timeOfDay = models.TimeField(
        default=time(0, 0),
        help_text="This field expects time in 24-hour format (HH:MM)."
    )
    endOfDay = models.TimeField(
        default=time(0, 0),
        help_text="This field expects time in 24-hour format (HH:MM)."
    )

    def __str__(self):
        return self.sectionName


class CourseInstructor(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE)

class SectionTA(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    ta = models.ForeignKey(User, on_delete=models.CASCADE)

