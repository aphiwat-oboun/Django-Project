from django.test import TestCase, Client
from django.urls import reverse
from .models import Student, Major
from .forms import StudentForm

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
