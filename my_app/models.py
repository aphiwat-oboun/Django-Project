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

# class Major
class Major(models.Model):
    major_name = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f'{self.major_name}'
    
    def get_absolute_url(self):
        return reverse('major_detail', kwargs={'pk': self.pk})
    

# stu_id FirstName LastName
class Student(models.Model):
    prefix_name = models.CharField(max_length=10, choices=PREFIX_NAME, default=1)
    stu_id = models.CharField(max_length=10, unique=True)
    fname = models.CharField(max_length=50, blank=True)
    lname = models.CharField(max_length=50, blank=True)
    major = models.ForeignKey(Major, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return f'{self.stu_id} {self.get_prefix_name_display()} {self.fname} {self.lname} {self.major}'
    
    def get_absolute_url(self):
        return reverse('student_detail', kwargs={'pk': self.pk})


# class Category (หมวดหมู่วิชา)
class Category(models.Model):
    category_name = models.CharField(max_length=100, unique=True, verbose_name="ชื่อหมวดหมู่วิชา")

    class Meta:
        verbose_name = "หมวดหมู่วิชา"
        verbose_name_plural = "หมวดหมู่วิชา"

    def __str__(self):
        return f'{self.category_name}'


# class Subject (รายวิชา)
class Subject(models.Model):
    subject_code = models.CharField(max_length=20, unique=True, verbose_name="รหัสวิชา")
    subject_name = models.CharField(max_length=150, verbose_name="ชื่อรายวิชา")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subjects", verbose_name="หมวดหมู่วิชา")

    class Meta:
        verbose_name = "รายวิชา"
        verbose_name_plural = "รายวิชา"
        ordering = ["subject_code"]

    def __str__(self):
        return f'{self.subject_code} - {self.subject_name}'

    def get_absolute_url(self):
        return reverse('subject_detail', kwargs={'pk': self.pk})


# Admin Registrations
class StudentAdmin(admin.ModelAdmin):
    list_display = ('get_prefix_name_display', 'stu_id', 'fname', 'lname', 'major')
    ordering = ('stu_id',)

admin.site.register(Student, StudentAdmin)

class MajorAdmin(admin.ModelAdmin):
    list_display = ('id', 'major_name')
    ordering = ('id',)

admin.site.register(Major, MajorAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category_name')
    ordering = ('id',)

admin.site.register(Category, CategoryAdmin)

class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_code', 'subject_name', 'category')
    list_filter = ('category',)
    search_fields = ('subject_code', 'subject_name')
    ordering = ('subject_code',)

admin.site.register(Subject, SubjectAdmin)