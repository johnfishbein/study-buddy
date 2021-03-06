import datetime
from django.test import TestCase, Client, LiveServerTestCase
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Profile, TutorCourse, StudentCourse, InAppMessage
from login.views import *
from login.forms import ProfileForm
#from selenium import webdriver
import unittest
import time


class UserModelTests(TestCase):
#TEST must begin with the string test
    def test_username_string(self):
        """
        input username is returned by to string method
        """
        tester = User(email="tester@virginia.edu")
        self.assertEqual(tester.__str__(), "")

class SimpleLogin(unittest.TestCase):
    def setUp(self):
        self.person = Profile(username = 'holly')
        self.person2 = Profile(username = 'hew', email = "tester@virginia.edu")
        
    def test_username(self):
        self.assertEqual(self.person.username, 'holly')
    def test_email_default(self):
        self.assertEqual(self.person.email, "")
    def test_email_nondefault(self):
        self.assertEqual(self.person2.email, "tester@virginia.edu")
    def test_pk(self):
        person3 = Profile(username = 'holly', pk = 1)
        self.assertEqual(person3.pk, 1)
        person3.delete()
    def test_pk_2(self):
        person3 = Profile(username = 'holly', pk = 1)
        person4 = Profile(username = 'holly', pk = 2)
        self.assertNotEqual(person3, person4)

class ClassFileTests(TestCase):
    def test_get_departments_fromtxt(self):
        departments = get_departments_fromtxt()
        self.assertEqual(len(departments.keys()), 9)
        self.assertEqual(len(departments['Engineering & Applied Sciences Departments']), 11)

    def test_get_courses(self):
        departments = get_departments_fromtxt()
        engineering = departments['Engineering & Applied Sciences Departments']
        link = engineering[0][0]
        courses = get_courses(link)
        self.assertNotEqual(len(courses), 0)

    def test_get_classes_fromtxt(self):
        classes = json.loads(get_classes_fromtxt())
        self.assertEqual(len(classes.values()), 3072)

    def test_departments(self):
        c = Client()
        response = c.get(reverse('login:departments'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['department_list']), 9)
        self.assertEqual(len(response.context['department_section_list']), 9)
        self.assertEqual(len(json.loads(response.context['classes'])), 3072)

    def test_get_department_section(self):
        c = Client()
        response = c.post(reverse('login:get_department_section'), {'choice': 'https://louslist.org/page.php?Semester=1202&Type=Group&Group=CompSci'}, follow=True)
        courses = c.session['courses']
        self.assertNotEqual(len(json.loads(courses)), 0)

class ClassSaveTests(TestCase):
    def test_parseCourse(self):
        course = "Tutor:CS 1110 - Introduction to Programming"
        parsed = parseCourse(course)
        self.assertEqual(parsed[0], 'CS')
        self.assertEqual(parsed[1], '1110')
        self.assertEqual(parsed[2], 'Introduction to Programming')

    def test_saveClasses(self):
        c = Client()
        postedItems = {'Tutor:CS 3240 - Advanced Software Development Techniques': 'course'}
        tester = User.objects.create(username='tester', password='12345', is_active=True, is_staff=True, is_superuser=True)
        tester.save()
        c.login(username='tester', password='12345')
        saveClasses(postedItems.items(), tester.id)
        self.assertNotEqual(len(TutorCourse.objects.filter(user=tester.profile)), 0)
        tester.delete()
    def test_not_save_Classes(self):
        c = Client()
        postedItems = {'Tutor:CS 3240 - Advanced Software Development Techniques': 'course'}
        tester = User.objects.create(username='tester', password='12345', is_active=True, is_staff=True, is_superuser=True)
        tester.save()
        tester2 = User.objects.create(username='tester2', password='123452', is_active=True, is_staff=True, is_superuser=True)
        tester2.save()
        c.login(username='tester', password='12345')
        saveClasses(postedItems.items(), tester.id)
        self.assertEqual(len(TutorCourse.objects.filter(user=tester2.profile)), 0)
        tester.delete()
        tester2.delete()

    # def test_userForm(self):
    #     c = Client()
    #     tester = User.objects.create(username='tester', password='12345', is_active=True, is_staff=True, is_superuser=True)
    #     tester.save()
    #     c.login(username='tester', password='12345')
    #     form = UserForm({
    #         'first_name': "tester2",
    #         'last_name': "lastname",
    #     }, instance=tester)
    #     self.assertTrue(form.is_valid())
    #     form.save()
    #     self.assertEqual(tester.first_name, "tester2")
    #     self.assertEqual(tester.last_name, "lastname")
    #     tester.delete()

    def test_profileForm(self):
        c = Client()
        tester = User.objects.create(username='tester', password='12345', is_active=True, is_staff=True, is_superuser=True)
        tester.save()
        c.login(username='tester', password='12345')
        form = ProfileForm({
            'first_name': "joe",
            'last_name': "joey",
            'username': "tester",
            'phone_number': "3018523444",
            'year': "Fourth",
            'bio': "testing",
            'location': "Inactive"
        }, instance=tester.profile)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(tester.profile.first_name, "joe")
        self.assertEqual(tester.profile.last_name, "joey")
        self.assertEqual(tester.profile.username, "tester")
        self.assertEqual(tester.profile.phone_number, "3018523444")
        tester.delete()

    def test_profileForm_case(self):
        c = Client()
        tester = User.objects.create(username='tester', password='12345', is_active=True, is_staff=True, is_superuser=True)
        tester.save()
        c.login(username='tester', password='12345')
        form = ProfileForm({
            'first_name': "Joe",
            'last_name': "Joey",
            'username': "Tester",
            'phone_number': "3018523444",
            'year': "Fourth",
            'bio': "testing",
            'location': "Inactive"
        }, instance=tester.profile)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertNotEqual(tester.profile.first_name, "joe")
        self.assertNotEqual(tester.profile.last_name, "joey")
        self.assertNotEqual(tester.profile.username, "tester")
        self.assertEqual(tester.profile.phone_number, "3018523444")
        tester.delete()
    def test_profileAndLogin(self):
        c = Client()
        tester = User.objects.create(username='tester1', password='12345', is_active=True, is_staff=True, is_superuser=True)
        tester.save()
        self.assertFalse(c.login(username='tester1', password='1234'))
        tester.delete()
    def test_profileAndLogin2(self):
        c = Client()
        tester = User.objects.create(username='tester1', password='12345', is_active=True, is_staff=False, is_superuser=True)
        tester.save()
        tester.delete()
        self.assertFalse(c.login(username='tester1', password='12345'))
    def test_profileAndLoginFail(self):
        c = Client()
        tester = User.objects.create(username='tester1', password='12345', is_active=True, is_staff=True, is_superuser=True)
        tester.save()
        self.assertFalse(c.login(username='test', password='1234'))
        tester.delete()
    def test_profileAndLoginFail2(self):
        c = Client()
        tester = User.objects.create(username='tester1', password='12345', is_active=True, is_staff=True, is_superuser=True)
        tester.save()
        tester2 = User.objects.create(username='test', password='1234', is_active=True, is_staff=True, is_superuser=True)
        tester2.save()
        self.assertFalse(c.login(username='tester1', password='1234'))
        tester.delete()
        tester2.delete()

class TutorSearch(unittest.TestCase):
    def test_single_course_search(self):
        c = Client()
        tester = User.objects.create(username='tester3', is_active=True, is_staff=True, is_superuser=True)
        tester.set_password('12345')
        tester.save()
        postedItems = {'Tutor:CS 3240 - Advanced Software Development Techniques': 'course'}
        c.login(username='tester3', password='12345')
        saveClasses(postedItems.items(), tester.id)
        response = c.post(reverse('login:home'), {'course': 'CS 3240 - Advanced Software Development Techniques'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['filtered_tutors']), 1)
        tester.delete()
    def test_single_course_search2(self):
        c = Client()
        tester = User.objects.create(username='tester3', is_active=True, is_staff=True, is_superuser=True)
        tester.set_password('12345')
        tester.save()
        postedItems = {'Tutor:CS 3240 - Advanced Software Development Techniques': 'course'}
        c.login(username='tester3', password='12345')
        response = c.post(reverse('login:home'), {'course': 'CS 3240 - Advanced Software Development Techniques'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertNotEqual(len(response.json()['filtered_tutors']), 1)
        tester.delete()
    def test_my_student_courses(self):
        c = Client()
        tester = User.objects.create(username='tester', is_active=True, is_staff=True, is_superuser=True)
        tester2 = User.objects.create(username='tester2', is_active=True, is_staff=True, is_superuser=True)
        tester.set_password('12345')
        tester.save()
        tester2.save()
        studentItems = {'Student:CS 3240 - Advanced Software Development Techniques': 'course', 'CBNameStudent:CS 1234 - Test Course': 'course'}
        tutorItems = {'Tutor:CS 3240 - Advanced Software Development Techniques': 'course'}
        saveClasses(studentItems.items(), tester.id)
        saveClasses(tutorItems.items(), tester2.id)
        c.login(username='tester', password='12345')
        studentCourses = ProfileSerializer(tester.profile).data['studentCourses']
        for i in range(len(studentCourses)):
            studentCourses[i] = StudentCourseSerializer(studentCourses[i]).data
        response = c.post(reverse('login:home'), {'courses': json.dumps(studentCourses)}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['filtered_tutors']), 1)
        tester.delete()
        tester2.delete()
    def test_request_tutor(self):
        c = Client()
        tester = User.objects.create(username='tester', is_active=True, is_staff=True, is_superuser=True)
        tester2 = User.objects.create(username='tester2', is_active=True, is_staff=True, is_superuser=True)
        tester.set_password('12345')
        tester.save()
        tester2.save()
        c.login(username='tester', password='12345')
        tutor = ProfileSerializer(tester2.profile).data
        response = c.post(reverse('login:home'), {'tutor': json.dumps(tutor), 'requestedCourse': "CS 1234 - Test Course", 'requestOption': "Request"}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(bool(response.json()['tutor']), True)
        inappmessages = list(InAppMessage.objects.filter(sender=tester.id))
        inappmessages += list(InAppMessage.objects.filter(recipient=tester.id))
        self.assertNotEqual(len(inappmessages), 0)
        tester.delete()
        tester2.delete()

class HomepageTest(unittest.TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_main(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)
    def test_main_fail(self):
        response = self.client.get('')
        self.assertNotEqual(response.status_code, 302)
    def test_profile(self):
        response = self.client.get('/profile')
        self.assertEqual(response.status_code, 302)
    def test_profile_fail(self):
        response = self.client.get('/profile')
        self.assertNotEqual(response.status_code, 200)

class RedirectTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()
    def test_redirect(self):
        response = self.client.get('/profile')
        self.assertRedirects(response, '/accounts/login/?next=/profile', status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)

class InAppMessageModelTests(TestCase):
    def test_in_app_message_model(self):
        tester = User(email="abc2@virginia.edu")
        tester2 = User(email="cba@virginia.edu", username="tester2")
        tester.save()
        tester2.save()
        inapp = InAppMessage(sender=tester.profile, recipient=tester2.profile, message= "This is a test message")
        inapp.save()
        self.assertEqual(inapp.message, "This is a test message")
        self.assertEqual(inapp.status, "unread")
        tester.delete()
        tester2.delete()
    def test_recipient(self):
        tester = User(email="abc2@virginia.edu")
        tester2 = User(email="cba@virginia.edu", username="tester2")
        tester.save()
        tester2.save()
        inapp = InAppMessage(sender=tester.profile, recipient=tester2.profile, message= "This is a test message")
        inapp.save()
        self.assertEqual(inapp.sender, tester.profile)
        self.assertEqual(inapp.recipient, tester2.profile)
        tester.delete()
        tester2.delete()
    def test_in_app_message_model_3user(self):
        tester = User(email="abc2@virginia.edu")
        tester2 = User(email="cba@virginia.edu", username="tester2")
        tester3 = User(email="abc@virginia.edu", username="tester3")
        tester.save()
        tester2.save()
        tester3.save()
        inapp = InAppMessage(sender=tester.profile, recipient=tester2.profile, message= "This is a test message")
        inapp.save()
        self.assertEqual(inapp.message, "This is a test message")
        self.assertEqual(inapp.status, "unread")
        inapp = InAppMessage(sender=tester.profile, recipient=tester3.profile, message= "This is a test message")
        inapp.save()
        self.assertEqual(inapp.message, "This is a test message")
        self.assertEqual(inapp.status, "unread")
        tester.delete()
        tester2.delete()
        tester3.delete()
    def test_in_app_message_model2messg(self):
        tester = User(email="abc2@virginia.edu")
        tester2 = User(email="cba@virginia.edu", username="tester2")
        tester.save()
        tester2.save()
        inapp = InAppMessage(sender=tester.profile, recipient=tester2.profile, message= "This is a test message")
        inapp.save()
        inapp2 = InAppMessage(sender=tester.profile, recipient=tester2.profile, message= "This is a 2nd test message")
        inapp2.save()
        self.assertEqual(inapp.message, "This is a test message")
        self.assertEqual(inapp.status, "unread")
        self.assertEqual(inapp2.message, "This is a 2nd test message")
        self.assertEqual(inapp2.status, "unread")
        tester.delete()
        tester2.delete()
    def test_in_app_message_model_empty(self):
        tester = User(email="abc2@virginia.edu")
        tester2 = User(email="cba@virginia.edu", username="tester2")
        tester.save()
        tester2.save()
        inapp = InAppMessage(sender=tester.profile, recipient=tester2.profile, message= "")
        inapp.save()
        self.assertEqual(inapp.message, "")
        self.assertEqual(inapp.status, "unread")
        tester.delete()
        tester2.delete()

class TutorCourseModelTests(TestCase):
    def test_tutor_course_model(self):
        tester = User(email="cba@virginia.edu", username="tester")
        tester.save()
        course = TutorCourse(name="CS 3240 - Advanced Software Development Techniques", dept="Computer Science", number=1234, user=tester.profile)
        course.save()
        self.assertEqual(course.name, "CS 3240 - Advanced Software Development Techniques")
        self.assertEqual(course.dept, "Computer Science")
        self.assertEqual(course.number, 1234)
        tester.delete()
    def test_tutor_course_model_2courses(self):
        tester = User(email="cba@virginia.edu", username="tester")
        tester.save()
        course = TutorCourse(name="CS 3240 - Advanced Software Development Techniques", dept="Computer Science", number=1234, user=tester.profile)
        course.save()
        course2 = TutorCourse(name="CS 1110 - Introduction to Programming", dept="Computer Science", number=2345, user=tester.profile)
        course2.save()
        self.assertEqual(course.name, "CS 3240 - Advanced Software Development Techniques")
        self.assertEqual(course.dept, "Computer Science")
        self.assertEqual(course.number, 1234)
        self.assertEqual(course2.name, "CS 1110 - Introduction to Programming")
        self.assertEqual(course2.dept, "Computer Science")
        self.assertEqual(course2.number, 2345)
        tester.delete()
    def test_tutor_course_model_2users(self):
        tester = User(email="cba@virginia.edu", username="tester")
        tester.save()
        tester2 = User(email="abc@virginia.edu", username="tester2")
        tester2.save()
        course = TutorCourse(name="CS 3240 - Advanced Software Development Techniques", dept="Computer Science", number=1234, user=tester.profile)
        course.save()
        course2 = TutorCourse(name="CS 3240 - Advanced Software Development Techniques", dept="Computer Science", number=1234, user=tester2.profile)
        course2.save()
        self.assertEqual(course.name, "CS 3240 - Advanced Software Development Techniques")
        self.assertEqual(course.dept, "Computer Science")
        self.assertEqual(course.number, 1234)
        self.assertEqual(course2.name, "CS 3240 - Advanced Software Development Techniques")
        self.assertEqual(course2.dept, "Computer Science")
        self.assertEqual(course2.number, 1234)
        tester.delete()

class StudentCourseModelTests(TestCase):
    def test_student_course_model(self):
        tester = User(email="cba@virginia.edu", username="tester")
        tester.save()
        course = StudentCourse(name="CS 3240 - Advanced Software Development Techniques", dept="Computer Science", number=1234, user=tester.profile)
        course.save()
        self.assertEqual(course.name, "CS 3240 - Advanced Software Development Techniques")
        self.assertEqual(course.dept, "Computer Science")
        self.assertEqual(course.number, 1234)
        tester.delete()
    def test_student_course_model_2courses(self):
        tester = User(email="cba@virginia.edu", username="tester")
        tester.save()
        course = StudentCourse(name="CS 3240 - Advanced Software Development Techniques", dept="Computer Science", number=1234, user=tester.profile)
        course.save()
        course2 = StudentCourse(name="CS 1110 - Introduction to Programming", dept="Computer Science", number=2345, user=tester.profile)
        course2.save()
        self.assertEqual(course.name, "CS 3240 - Advanced Software Development Techniques")
        self.assertEqual(course.dept, "Computer Science")
        self.assertEqual(course.number, 1234)
        self.assertEqual(course2.name, "CS 1110 - Introduction to Programming")
        self.assertEqual(course2.dept, "Computer Science")
        self.assertEqual(course2.number, 2345)
        tester.delete()
    def test_student_course_model_2users(self):
        tester = User(email="cba@virginia.edu", username="tester")
        tester.save()
        tester2 = User(email="abc@virginia.edu", username="tester2")
        tester2.save()
        course = StudentCourse(name="CS 3240 - Advanced Software Development Techniques", dept="Computer Science", number=1234, user=tester.profile)
        course.save()
        course2 = StudentCourse(name="CS 3240 - Advanced Software Development Techniques", dept="Computer Science", number=1234, user=tester2.profile)
        course2.save()
        self.assertEqual(course.name, "CS 3240 - Advanced Software Development Techniques")
        self.assertEqual(course.dept, "Computer Science")
        self.assertEqual(course.number, 1234)
        self.assertEqual(course2.name, "CS 3240 - Advanced Software Development Techniques")
        self.assertEqual(course2.dept, "Computer Science")
        self.assertEqual(course2.number, 1234)
        tester.delete()

class RedirectTests(TestCase):
    def setUp(self):
        self.client = Client()
    def test_redirect(self):
        response = self.client.get('/profile')
        self.assertRedirects(response, '/accounts/login/?next=/profile', status_code=302, target_status_code=200, msg_prefix='', fetch_redirect_response=True)
