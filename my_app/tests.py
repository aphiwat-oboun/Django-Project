from django.test import TestCase, Client
from django.urls import reverse
from .models import Student, Major, Category, Subject
from .forms import StudentForm, SubjectForm

class StudentCRUDTestCase(TestCase):
    def setUp(self):
        self.client = Client()
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
