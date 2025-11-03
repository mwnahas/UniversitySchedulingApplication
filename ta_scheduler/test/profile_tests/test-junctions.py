from django.test import TestCase
from django.utils import timezone
from ta_scheduler.models import Course, Section, CourseInstructor, SectionTA, User

class JunctionModelTests(TestCase):
    def setUp(self):
        self.instructor1 = User.objects.create_user(username='instructor1', full_name='Instructor One', role='instructor')
        self.instructor2 = User.objects.create_user(username='instructor2', full_name='Instructor Two', role='instructor')
        self.ta1 = User.objects.create_user(username='ta1', full_name='TA One', role='ta')
        self.ta2 = User.objects.create_user(username='ta2', full_name='TA Two', role='ta')

        self.course = Course.objects.create(courseName='CS101', semester='fall', year=2025)
        self.section = Section.objects.create(
            sectionName='S1',
            dayOfWeek='1',
            course=self.course,
            timeOfDay=timezone.now().time(),
            endOfDay=timezone.now().time()
        )

    def test_multiple_instructors_per_course(self):
        # assign both instructors to the same course
        CourseInstructor.objects.create(course=self.course, instructor=self.instructor1)
        CourseInstructor.objects.create(course=self.course, instructor=self.instructor2)

        instructors = CourseInstructor.objects.filter(course=self.course).values_list('instructor__username', flat=True)
        self.assertIn('instructor1', instructors)
        self.assertIn('instructor2', instructors)
        self.assertEqual(len(instructors), 2)

    def test_multiple_tas_per_section(self):
        # assign both TAs to the same section
        SectionTA.objects.create(section=self.section, ta=self.ta1)
        SectionTA.objects.create(section=self.section, ta=self.ta2)

        tas = SectionTA.objects.filter(section=self.section).values_list('ta__username', flat=True)
        self.assertIn('ta1', tas)
        self.assertIn('ta2', tas)
        self.assertEqual(len(tas), 2)