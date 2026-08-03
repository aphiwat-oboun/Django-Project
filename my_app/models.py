# pyrefly: ignore [missing-import]
from django.db import models
# pyrefly: ignore [missing-import]
from django.urls import reverse
# pyrefly: ignore [missing-import]
from django.contrib import admin

PREFIX_NAME = (
    ("1", "นาย"),
    ("2", "นาง"),
    ("3", "นางสาว"),
)

# stu_id FirstName LastName
class Student(models.Model):
    prefix_name = models.CharField(max_length=10, choices=PREFIX_NAME, default=1)
    stu_id = models.CharField(max_length=10, unique=True)
    fname = models.CharField(max_length=50, blank=True)
    lname = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f'{self.stu_id} {self.get_prefix_name_display()} {self.fname} {self.lname}'
    
    def get_absolute_url(self):
        return reverse('student_detail', kwargs={'pk': self.pk})

class StudentAdmin(admin.ModelAdmin):
    list_display = ('stu_id', 'get_prefix_name_display', 'fname', 'lname')

admin.site.register(Student, StudentAdmin)
