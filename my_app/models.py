from django.db import models
from django.urls import reverse
from django.contrib import admin
from django.utils.html import format_html

PREFIX_NAME = (
    ("1", "นาย"),
    ("2", "นาง"),
    ("3", "นางสาว"),
)

SEMESTER = (
    ("1/2569", "1/2569"),
    ("2/2569", "2/2569"),
    ("3/2569", "3/2569"),
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

class Enrolls(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrolls", verbose_name="นักศึกษา")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="enrolls", verbose_name="รายวิชา")
    semester = models.CharField(max_length=10, choices=SEMESTER, default="1/2569")

    class Meta:
        verbose_name = "Enrolls"
        verbose_name_plural = "Enrolls"
        ordering = ["semester"]
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'subject', 'semester'],
                name='unique_student_subject_semester'
            )
        ]

    def __str__(self):
        return f'{self.student} - {self.subject}'

    def get_absolute_url(self):
        return reverse('enrolls_detail', kwargs={'pk': self.pk})

class EnrollsInline(admin.TabularInline):
    model = Enrolls
    extra = 1
    autocomplete_fields = ['subject']
    verbose_name = "รายวิชาที่ลงทะเบียน"
    verbose_name_plural = "รายวิชาที่ลงทะเบียน (Enrolls)"

class EnrollsAdmin(admin.ModelAdmin):
    list_display = (
        'get_stu_id',
        'get_student_name',
        'get_major',
        'get_subject_code',
        'get_subject_name',
        'semester',
    )
    list_filter = ('semester', 'subject__category', 'student__major')
    search_fields = (
        'student__stu_id',
        'student__fname',
        'student__lname',
        'subject__subject_code',
        'subject__subject_name',
    )
    autocomplete_fields = ['student', 'subject']
    ordering = ('-semester', 'student__stu_id')
    list_per_page = 20

    @admin.display(description="รหัสนักศึกษา", ordering="student__stu_id")
    def get_stu_id(self, obj):
        return obj.student.stu_id

    @admin.display(description="ชื่อ - นามสกุล", ordering="student__fname")
    def get_student_name(self, obj):
        return f"{obj.student.get_prefix_name_display()} {obj.student.fname} {obj.student.lname}"

    @admin.display(description="สาขาวิชา", ordering="student__major__major_name")
    def get_major(self, obj):
        return obj.student.major.major_name

    @admin.display(description="รหัสวิชา", ordering="subject__subject_code")
    def get_subject_code(self, obj):
        return obj.subject.subject_code

    @admin.display(description="ชื่อรายวิชา", ordering="subject__subject_name")
    def get_subject_name(self, obj):
        return obj.subject.subject_name

# Admin Registrations
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'stu_id',
        'get_full_name',
        'major',
        'get_enrolled_subjects_badges',
        'get_enrolled_count',
    )
    search_fields = (
        'stu_id',
        'fname',
        'lname',
        'enrolls__subject__subject_code',
        'enrolls__subject__subject_name',
    )
    list_filter = ('major', 'prefix_name', 'enrolls__semester')
    ordering = ('stu_id',)
    inlines = [EnrollsInline]
    list_per_page = 20

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('major').prefetch_related('enrolls__subject')

    @admin.display(description="ชื่อ - นามสกุล", ordering="fname")
    def get_full_name(self, obj):
        return f"{obj.get_prefix_name_display()} {obj.fname} {obj.lname}"

    @admin.display(description="รายวิชาที่ลงทะเบียน")
    def get_enrolled_subjects_badges(self, obj):
        enrolls = obj.enrolls.all()
        if not enrolls:
            return format_html('<span style="color: #64748b; font-size: 0.8rem; font-style: italic;">ยังไม่ได้ลงทะเบียน</span>')
        
        badges = []
        for e in enrolls:
            badges.append(
                f'<span style="background: rgba(99, 102, 241, 0.15); color: #818cf8; border: 1px solid rgba(129, 140, 248, 0.35); '
                f'padding: 3px 8px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; margin: 2px; display: inline-block;" '
                f'title="{e.subject.subject_name} ({e.semester})">'
                f'{e.subject.subject_code} <span style="font-weight: 400; opacity: 0.75; font-size: 0.75rem;">({e.semester})</span></span>'
            )
        return format_html(" ".join(badges))

    @admin.display(description="รวม (วิชา)")
    def get_enrolled_count(self, obj):
        count = obj.enrolls.count()
        if count > 0:
            return format_html(
                '<span style="background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.35); '
                'font-weight: 700; padding: 2px 10px; border-radius: 12px; font-size: 0.8rem;">{} วิชา</span>',
                count
            )
        return format_html('<span style="color: #64748b; font-size: 0.8rem;">0 วิชา</span>')

class MajorAdmin(admin.ModelAdmin):
    list_display = ('id', 'major_name')
    ordering = ('id',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category_name')
    ordering = ('id',)

class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_code', 'subject_name', 'category')
    list_filter = ('category',)
    search_fields = ('subject_code', 'subject_name')
    ordering = ('subject_code',)

admin.site.register(Major, MajorAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Enrolls, EnrollsAdmin)