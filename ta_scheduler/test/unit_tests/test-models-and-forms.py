from django.test import TestCase

from ta_scheduler import views
from ta_scheduler.models import User
from datetime import time
from ta_scheduler.models import Section
from ta_app.forms import SectionForm, CourseForm, SectionAdminForm
from django.contrib.auth.models import Group
from ta_scheduler.models import Course, CourseInstructor
from django.urls import reverse
from unittest.mock import *


#unit tests for models and forms
class SectionModelTest(TestCase):
    def setUp(self):
        self.ta = User.objects.create_user(username='tauser', password='testpass')
        self.course = Course.objects.create(courseName='CS101', semester= 'spring', year = 2025)
        self.section = Section.objects.create(
            course = self.course,
            sectionName='Lab A',
            dayOfWeek='1',  # Monday
            teaching_assistant=self.ta,
            timeOfDay=time(14, 30),
            endOfDay=time(15,30),
        )

    def test_create_section(self):
        section = Section.objects.create(
            sectionName='Lab A',
            dayOfWeek='1',  # Monday
            teaching_assistant=self.ta,
            timeOfDay=time(14, 30)
        )
        self.assertEqual(section.sectionName, 'Lab A')
        self.assertEqual(section.dayOfWeek, '1')
        self.assertEqual(section.teaching_assistant.username, 'tauser')
        self.assertEqual(section.timeOfDay, time(14, 30))

    def test_create_section_without_ta(self):
        section = Section.objects.create(
            sectionName='No TA Lab',
            dayOfWeek='1',
            timeOfDay=time(9, 0)
        )
        self.assertIsNone(section.teaching_assistant)
        self.assertEqual(section.sectionName, 'No TA Lab')
        self.assertEqual(section.dayOfWeek, '1')


class CourseModelTest(TestCase):
    def setUp(self):
        # Create a user for instructor (though not used directly in Course)
        self.instructor = User.objects.create_user(username='instructor', password='test', is_staff=True)

        #also creating a TA, required for some tests
        self.teaching_assistant = User.objects.create(username = 'NewTA', password = 'test', is_staff=False)

        # Create a course
        self.course = Course.objects.create(
            courseName='Intro to CS',
            semester = 'spring',
            year = 2025,
        )

    def test_create_course(self):
        # Test creating a course with a valid name
        self.assertEqual(self.course.courseName, 'Intro to CS')

    def test_course_str_method(self):
        # Test the __str__ method of the Course model
        self.assertEqual(str(self.course), 'Intro to CS (Spring 2025)')

    def test_create_multiple_courses(self):
        # Test creating multiple courses
        course2 = Course.objects.create(courseName='Data Structures', semester = 'spring', year = 2025,)
        course3 = Course.objects.create(courseName='Algorithms', semester = 'spring', year = 2025)

        self.assertEqual(course2.courseName, 'Data Structures')
        self.assertEqual(course3.courseName, 'Algorithms')

    def test_delete_course(self):
        #fields for instructor are deleted since they are no longer used
        #courses no longer have any fields other than courseName
        #these tests are still valid, but are updated to align with our current design
        course = Course.objects.create(
            courseName='Deletable Course',
            semester = 'spring',
            year = 2025,
        )
        course_id = course.id
        course.delete()
        with self.assertRaises(Course.DoesNotExist):
            Course.objects.get(id=course_id)

    def test_delete_section_and_check_course(self):
        # Create a course with a section, then delete the section
        newSection = Section.objects.create(
            sectionName='EE305',
            dayOfWeek='1',
            course = self.course,
            teaching_assistant= self.teaching_assistant,
            instructor = self.instructor,
            timeOfDay = '00:00',
            endOfDay = '00:00'
        )
        # courses and sections are joined together by the section object
        # section objects have a field for the course they are a part of,
        # we don't particularly care about courses belonging to any instance
        # of a section, only the other way around
        F = self.course.sections.exists()
        newSection.delete()
        F = self.course.sections.exists()
        self.course.refresh_from_db()
        self.assertFalse(self.course.sections.exists())

    def test_multiple_sections(self):
        labSection_1 = Section.objects.create(
            sectionName='EE305-801',
            dayOfWeek='1',
            course=self.course,
            teaching_assistant=self.teaching_assistant,
            instructor=self.instructor,
            timeOfDay='00:00',
            endOfDay='00:00'
        )

        labSection_2 = Section.objects.create(
            sectionName='EE305-802',
            dayOfWeek='4',
            course=self.course,
            teaching_assistant=self.teaching_assistant,
            instructor=self.instructor,
            timeOfDay='12:00',
            endOfDay='1:45'
        )
        self.assertTrue(self.course.sections.contains(labSection_2))
        self.assertTrue(self.course.sections.contains(labSection_1))

    def test_change_year(self):
        self.course.year = 2026
        self.course.save()
        self.assertEqual(self.course.year, 2026)

    def test_change_semester(self):
        self.course.semester = 'fall'
        self.course.save()
        self.assertEqual(self.course.semester, 'fall')

    def test_change_course_name(self):
        self.course.courseName = 'CS 361'
        self.course.save()
        self.assertEqual(self.course.courseName, 'CS 361')



class SectionFormTest(TestCase):
    def setUp(self):
        self.ta = User.objects.create_user(username='ta', password='test')

    def test_valid_section_form(self):
        form = SectionForm(data={
            'sectionName': 'Lab C',
            'dayOfWeek': '3',
            'teaching_assistant': self.ta.id,
            'timeOfDay': '15:00'
        })
        self.assertTrue(form.is_valid())

    def test_invalid_section_form_missing_time(self):
        form = SectionForm(data={
            'sectionName': 'Lab D',
            'dayOfWeek': '4',
            'teaching_assistant': self.ta.id
            # timeOfDay is missing
        })
        self.assertFalse(form.is_valid())
        self.assertIn('timeOfDay', form.errors)

    def test_delete_section(self):
        section = Section.objects.create(
            sectionName='Lab Delete',
            dayOfWeek='2',
            teaching_assistant=self.ta,
            timeOfDay=time(13, 0)
        )
        section_id = section.id
        section.delete()
        with self.assertRaises(Section.DoesNotExist):
            Section.objects.get(id=section_id)


class CourseFormTest(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(username='instructor', password='test', is_staff=True)
        self.course = Course.objects.create(courseName='Data Structures', semester = 'spring', year = 2025)


    def test_valid_course_form(self):
        form = CourseForm(data={
            'courseName': 'Data Structures',
            'semester': 'spring',
            'year': '2025'
        })
        self.assertTrue(form.is_valid())

#testing that users are filtered by group
class SectionAdminFormTest(TestCase):
    def setUp(self):
        # Create group and assign one user
        self.ta_group = Group.objects.create(name='Teaching Assistants')
        self.ta_user = User.objects.create_user(username='ta_user')
        self.other_user = User.objects.create_user(username='not_ta_user')
        self.ta_group.user_set.add(self.ta_user)

    def test_teaching_assistant_queryset_filtered_by_group(self):
        form = SectionAdminForm()
        self.assertIn(self.ta_user, form.fields['teaching_assistant'].queryset)
        self.assertNotIn(self.other_user, form.fields['teaching_assistant'].queryset)

#removed test for course, since it no loger has an instructor field

class CourseInstructorTests(TestCase):
    def setUp(self):
        # Create instructor
        self.bob = User.objects.create_user(username='bob', password='testpass')
        self.alice = User.objects.create_user(username='alice', password='testpass')

        # Create courses
        self.cs101 = Course.objects.create(courseName="CS101", semester = 'spring', year = 2025)
        self.cs102 = Course.objects.create(courseName="CS102", semester = 'spring', year = 2025)

        # Assign bob to two courses
        CourseInstructor.objects.create(course=self.cs101, instructor=self.bob)
        CourseInstructor.objects.create(course=self.cs102, instructor=self.bob)

        # Assign alice to one course
        CourseInstructor.objects.create(course=self.cs101, instructor=self.alice)

    def test_instructor_teaches_multiple_courses(self):
        courses = [ci.course for ci in CourseInstructor.objects.filter(instructor=self.bob)]
        self.assertEqual(len(courses), 2)
        self.assertIn(self.cs101, courses)
        self.assertIn(self.cs102, courses)

    def test_course_has_multiple_instructors(self):
        instructors = [ci.instructor for ci in CourseInstructor.objects.filter(course=self.cs101)]
        self.assertEqual(len(instructors), 2)
        self.assertIn(self.bob, instructors)
        self.assertIn(self.alice, instructors)

    def test_instructor_removed_from_course(self):
        # course objects have nothing but a name,
        # we use another table in the database to map instructors and courses together
        instructors = [ci.instructor for ci in CourseInstructor.objects.filter(course=self.cs101)]
        self.assertIn(self.alice, instructors)
        User.delete(self.alice)
        instructors = [ci.instructor for ci in CourseInstructor.objects.filter(course=self.cs101)]
        self.assertNotIn(self.alice, instructors)

    def test_instructor_added_after_creation(self):
        newInstructor = User.objects.create(username = 'test', password = 'test', full_name= 'New Instructor')
        CourseInstructor.objects.create(course = self.cs101, instructor = newInstructor)
        instructors = [cs101_instructors.instructor for cs101_instructors in CourseInstructor.objects.filter(course = self.cs101)]
        self.assertIn(newInstructor, instructors)

    def test_delete_course_to_instructor_mapping(self):
        # deleting a course should delete all the instructors that teach that course
        self.cs101.delete()
        self.cs101.save()
        instructors = [cs101_instructors.instructor for cs101_instructors in CourseInstructor.objects.filter(course=self.cs101)]
        self.assertEqual(len(instructors), 0)

    def test_get_course_from_instructor(self):
        courses = [myCourse.course for myCourse in CourseInstructor.objects.filter(instructor= self.bob)]
        self.assertIn(self.cs101, courses)

    def test_delete_course_from_instructor(self):
        courses = [myCourse.course for myCourse in CourseInstructor.objects.filter(instructor = self.alice)]
        self.assertIn(self.cs101, courses)
        #alice is part of cs101
        self.cs101.delete()
        self.cs101.save()
        self.assertNotIn(self.cs101, courses)

class SectionTemplate(TestCase):
    def setUp(self):
        self.myCourse = Course.objects.create(
            courseName= 'CS101',
            year = 2025,
            semester = 'spring',
        )
        self.mySection = Section.objects.create(
            course= self.myCourse,
            sectionName = '801',
            instructor = User.objects.create(username = 'instructor', password= 'instructor'),
            dayOfWeek='1',
            timeOfDay='12:00:00',
            teaching_assistant= User.objects.create(username = 'ta', password = 'ta')
        )
        self.myUser = User.objects.create_user(username='Admin', password = 'Admin')
        response = self.client.login(username = 'Admin', password = 'Admin')
        response = self.client.get(reverse('courses'), follow = True)

    def fake_sectionEdit(self, request, section_id):
        self.mySection = Section.objects.get(id=section_id)
        self.mySection.sectionName = "CS101-802"
        self.mySection.save()
        return MagicMock(status_code=200, content='{"section_name": "CS101-802"}')


    @patch("ta_scheduler.views.sectionEdit")
    def test_edit_section_name(self, mock_edit_section):
        mock_edit_section.side_effect = self.fake_sectionEdit
        post_data = {'sectionName', 'CS101-802'}
        post_response = self.fake_sectionEdit(None, self.mySection.id)
        self.assertEqual(post_response.status_code, 200)

    @patch("ta_scheduler.views.sectionEdit")
    def test_edit_section_instructor(self, mock_edit_section):
        mock_edit_section.side_effect = self.fake_sectionEdit
        post_data = {'instructor', 'Jim Belushi'}
        post_response = self.fake_sectionEdit(None, self.mySection.id)
        self.assertEqual(post_response.status_code, 200)

    @patch("ta_scheduler.views.sectionEdit")
    def test_edit_section_time(self, mock_edit_section):
        mock_edit_section.side_effect = self.fake_sectionEdit
        post_data = {'timeOfDay', '01:00:00'}
        post_response = self.fake_sectionEdit(None, self.mySection.id)
        self.assertEqual(post_response.status_code, 200)

    @patch("ta_scheduler.views.sectionEdit")
    def test_edit_section_dayofweek(self, mock_edit_section):
        mock_edit_section.side_effect = self.fake_sectionEdit
        post_data = {'dayOfWeek', '2'}
        post_response = self.fake_sectionEdit(None, self.mySection.id)
        self.assertEqual(post_response.status_code, 200)

    @patch("ta_scheduler.views.sectionEdit")
    def test_edit_section_TA(self, mock_edit_section):
        mock_edit_section.side_effect = self.fake_sectionEdit
        post_data = {'teaching_assistant', 'Dua Lipa'}
        post_response = self.fake_sectionEdit(None, self.mySection.id)
        self.assertEqual(post_response.status_code, 200)