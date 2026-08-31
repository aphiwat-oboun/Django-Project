from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Student, Major, Category, Subject
from .forms import StudentForm, SubjectForm, RegisterForm

class StudentCRUDTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client.force_login(self.user)
        self.major = Major.objects.create(major_name="Computer Science")
        self.student = Student.objects.create(
            prefix_name="1",
            stu_id="6500000001",
            fname="Somchai",
            lname="Jaidee",
            major=self.major
        )

    def test_student_list_view(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "6500000001")
        self.assertContains(response, "Somchai")

    def test_student_detail_view(self):
        response = self.client.get(reverse("student_detail", kwargs={"pk": self.student.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "6500000001")
        self.assertContains(response, "Somchai")

    def test_student_create_get(self):
        response = self.client.get(reverse("student_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "student_form.html")

    def test_student_create_post(self):
        data = {
            "prefix_name": "3",
            "stu_id": "6500000002",
            "fname": "Somsri",
            "lname": "Deejai",
            "major": self.major.pk,
        }
        response = self.client.post(reverse("student_create"), data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Student.objects.filter(stu_id="6500000002").exists())
        created_student = Student.objects.get(stu_id="6500000002")
        self.assertEqual(created_student.fname, "Somsri")

    def test_student_update_post(self):
        data = {
            "prefix_name": "1",
            "stu_id": "6500000001",
            "fname": "Somchai_Updated",
            "lname": "Jaidee",
            "major": self.major.pk,
        }
        response = self.client.post(
            reverse("student_update", kwargs={"pk": self.student.pk}),
            data=data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.student.refresh_from_db()
        self.assertEqual(self.student.fname, "Somchai_Updated")

    def test_student_delete_post(self):
        pk = self.student.pk
        response = self.client.post(
            reverse("student_delete", kwargs={"pk": pk}),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Student.objects.filter(pk=pk).exists())


class SubjectCRUDTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser_subject", password="password123")
        self.client.force_login(self.user)
        self.category = Category.objects.create(category_name="วิชาเฉพาะสาขา")
        self.subject = Subject.objects.create(
            subject_code="CS101",
            subject_name="พื้นฐานวิทยาการคอมพิวเตอร์",
            category=self.category
        )

    def test_subject_list_view(self):
        response = self.client.get(reverse("subject_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CS101")
        self.assertContains(response, "พื้นฐานวิทยาการคอมพิวเตอร์")

    def test_subject_list_filter(self):
        response = self.client.get(reverse("subject_list") + f"?category={self.category.id}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CS101")

    def test_subject_detail_view(self):
        response = self.client.get(reverse("subject_detail", kwargs={"pk": self.subject.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CS101")
        self.assertContains(response, "พื้นฐานวิทยาการคอมพิวเตอร์")

    def test_subject_create_get(self):
        response = self.client.get(reverse("subject_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "subject_form.html")

    def test_subject_create_post(self):
        data = {
            "subject_code": "CS102",
            "subject_name": "การเขียนโปรแกรมเบื้องต้น (Python)",
            "category": self.category.pk,
        }
        response = self.client.post(reverse("subject_create"), data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Subject.objects.filter(subject_code="CS102").exists())

    def test_subject_update_post(self):
        data = {
            "subject_code": "CS101",
            "subject_name": "พื้นฐานวิทยาการคอมพิวเตอร์ (ปรับปรุง)",
            "category": self.category.pk,
        }
        response = self.client.post(
            reverse("subject_update", kwargs={"pk": self.subject.pk}),
            data=data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.subject.refresh_from_db()
        self.assertEqual(self.subject.subject_name, "พื้นฐานวิทยาการคอมพิวเตอร์ (ปรับปรุง)")

    def test_subject_delete_post(self):
        pk = self.subject.pk
        response = self.client.post(
            reverse("subject_delete", kwargs={"pk": pk}),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Subject.objects.filter(pk=pk).exists())


class AuthTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="adminuser", password="securepassword123")

    def test_login_page_get(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")

    def test_login_success(self):
        response = self.client.post(reverse("login"), {
            "username": "adminuser",
            "password": "securepassword123",
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_authenticated)

    def test_login_invalid_password(self):
        response = self.client.post(reverse("login"), {
            "username": "adminuser",
            "password": "wrongpassword",
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["user"].is_authenticated)
        self.assertContains(response, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

    def test_register_page_get(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")

    def test_register_success(self):
        response = self.client.post(reverse("register"), {
            "username": "new_student",
            "email": "student@university.ac.th",
            "password": "mypassword123",
            "confirm_password": "mypassword123",
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username="new_student").exists())
        self.assertTrue(response.context["user"].is_authenticated)

    def test_social_login_google(self):
        response = self.client.get(reverse("social_login", kwargs={"provider": "google"}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertEqual(response.context["user"].username, "google_user")

    def test_social_login_line(self):
        response = self.client.get(reverse("social_login", kwargs={"provider": "line"}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_authenticated)
        self.assertEqual(response.context["user"].username, "line_user")

    def test_logout(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("logout"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["user"].is_authenticated)
