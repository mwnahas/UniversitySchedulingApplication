from django.contrib import admin

from ta_scheduler.models import Course, Section, User, CourseInstructor, PublicProfile, SectionTA

# Register your models here.

admin.site.register(Course)
admin.site.register(Section)
admin.site.register(User)
admin.site.register(CourseInstructor)
admin.site.register(SectionTA)


@admin.register(PublicProfile)
class PublicProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'email', 'office_location', 'office_hours', 'bio']
    search_fields = ['user__username']