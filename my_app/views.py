# pyrefly: ignore [missing-import]
from django.shortcuts import render, get_object_or_404, redirect
# pyrefly: ignore [missing-import]
from django.contrib import messages
# pyrefly: ignore [missing-import]
from django.db.models import Q
# pyrefly: ignore [missing-import]
from django.core.paginator import Paginator
# pyrefly: ignore [missing-import]
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
import datetime
from .models import Student, Major, Category, Subject, Enrolls, SEMESTER
from .forms import StudentForm, SubjectForm, RegisterForm, EnrollsForm

def home(request):
    q = request.GET.get("q", "").strip()
    major_id = request.GET.get("major", "").strip()
    
    students_list = Student.objects.select_related("major").all().order_by("id")
    
    if q:
        students_list = students_list.filter(
            Q(stu_id__icontains=q) |
            Q(fname__icontains=q) |
            Q(lname__icontains=q)
        )
    
    if major_id:
        students_list = students_list.filter(major_id=major_id)

    # Pagination (10 students per page)
    paginator = Paginator(students_list, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    total_students = Student.objects.count()
    total_majors = Major.objects.count()
    total_subjects = Subject.objects.count()

    context = {
        "title": "รายชื่อนักศึกษา (Student List)",
        "students": page_obj.object_list,
        "page_obj": page_obj,
        "paginator": paginator,
        "majors": Major.objects.all().order_by("id"),
        "selected_major": major_id,
        "search_query": q,
        "total_students": total_students,
        "total_majors": total_majors,
        "total_subjects": total_subjects,
        "date": datetime.datetime.today(),
    }
    return render(request, "index.html", context)


def about(request):
    context = {
        "title": "About",
    }
    return render(request, "about.html", context)


def contact(request):
    context = {
        "title": "Contact",
    }
    return render(request, "contact.html", context)


# ---------------- Student CRUD & Enrollment ----------------
def student_detail(request, pk):
    student = get_object_or_404(Student.objects.select_related("major"), pk=pk)
    enrolls = student.enrolls.select_related("subject", "subject__category").all().order_by("semester", "subject__subject_code")
    all_subjects = Subject.objects.select_related("category").all().order_by("subject_code")
    enroll_form = EnrollsForm()

    context = {
        "title": f"ข้อมูลนักศึกษา: {student.get_prefix_name_display()}{student.fname} {student.lname}",
        "student": student,
        "enrolls": enrolls,
        "all_subjects": all_subjects,
        "semesters": SEMESTER,
        "enroll_form": enroll_form,
        "date": datetime.datetime.today(),
    }

    return render(request, "student_detail.html", context)


@login_required
def student_create(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(request, f"เพิ่มข้อมูลนักศึกษา {student.fname} {student.lname} เรียบร้อยแล้ว")
            return redirect("home")
        else:
            messages.error(request, "กรุณาตรวจสอบข้อมูลที่กรอกอีกครั้ง")
    else:
        form = StudentForm()
    
    context = {
        "title": "เพิ่มข้อมูลนักศึกษา (Add Student)",
        "form": form,
        "action": "create",
        "date": datetime.datetime.today(),
    }
    return render(request, "student_form.html", context)


@login_required
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            student = form.save()
            messages.success(request, f"แก้ไขข้อมูลนักศึกษา {student.fname} {student.lname} เรียบร้อยแล้ว")
            return redirect("student_detail", pk=student.pk)
        else:
            messages.error(request, "กรุณาตรวจสอบข้อมูลที่กรอกอีกครั้ง")
    else:
        form = StudentForm(instance=student)
    
    context = {
        "title": f"แก้ไขข้อมูลนักศึกษา: {student.fname} {student.lname}",
        "form": form,
        "student": student,
        "action": "update",
        "date": datetime.datetime.today(),
    }
    return render(request, "student_form.html", context)


@login_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        student_name = f"{student.fname} {student.lname}"
        student.delete()
        messages.success(request, f"ลบข้อมูลนักศึกษา {student_name} เรียบร้อยแล้ว")
        return redirect("home")
    
    context = {
        "title": f"ยืนยันการลบข้อมูลนักศึกษา: {student.fname} {student.lname}",
        "student": student,
        "date": datetime.datetime.today(),
    }
    return render(request, "student_confirm_delete.html", context)


# ---------------- Enrollment Actions (ลงทะเบียนเรียน) ----------------
@login_required
def enroll_create(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    if request.method == "POST":
        form = EnrollsForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get("subject")
            semester = form.cleaned_data.get("semester")

            # Check for duplicate enrollment in same semester
            if Enrolls.objects.filter(student=student, subject=subject, semester=semester).exists():
                messages.warning(request, f"นักศึกษาได้ลงทะเบียนวิชา {subject.subject_code} ในภาคเรียน {semester} ไปแล้ว")
            else:
                enroll = form.save(commit=False)
                enroll.student = student
                enroll.save()
                messages.success(request, f"ลงทะเบียนวิชา {subject.subject_code} ({subject.subject_name}) ภาคเรียน {semester} สำเร็จ")
        else:
            messages.error(request, "กรุณาเลือกรายวิชาและภาคเรียนให้ถูกต้อง")

    return redirect("student_detail", pk=student.pk)


@login_required
def enroll_delete(request, pk):
    enroll = get_object_or_404(Enrolls.objects.select_related("student", "subject"), pk=pk)
    student_id = enroll.student.pk
    if request.method == "POST":
        subject_name = f"{enroll.subject.subject_code} - {enroll.subject.subject_name}"
        semester = enroll.semester
        enroll.delete()
        messages.success(request, f"ถอนการลงทะเบียนวิชา {subject_name} (ภาคเรียน {semester}) เรียบร้อยแล้ว")

    return redirect("student_detail", pk=student_id)


# ---------------- Subject CRUD ----------------
def subject_list(request):
    q = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()

    subjects_list = Subject.objects.select_related("category").all().order_by("subject_code")

    if q:
        subjects_list = subjects_list.filter(
            Q(subject_code__icontains=q) |
            Q(subject_name__icontains=q)
        )
    
    if category_id:
        subjects_list = subjects_list.filter(category_id=category_id)

    # Pagination (10 subjects per page)
    paginator = Paginator(subjects_list, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    total_subjects = Subject.objects.count()
    total_categories = Category.objects.count()

    context = {
        "title": "รายวิชาทั้งหมด (Course Curriculum)",
        "subjects": page_obj.object_list,
        "page_obj": page_obj,
        "paginator": paginator,
        "categories": Category.objects.all().order_by("id"),
        "selected_category": category_id,
        "search_query": q,
        "total_subjects": total_subjects,
        "total_categories": total_categories,
        "date": datetime.datetime.today(),
    }
    return render(request, "subject_list.html", context)


def subject_detail(request, pk):
    subject = get_object_or_404(Subject.objects.select_related("category"), pk=pk)

    context = {
        "title": f"ข้อมูลรายวิชา: {subject.subject_code} - {subject.subject_name}",
        "subject": subject,
        "date": datetime.datetime.today(),
    }
    return render(request, "subject_detail.html", context)


@login_required
def subject_create(request):
    if request.method == "POST":
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save()
            messages.success(request, f"เพิ่มรายวิชา {subject.subject_code} ({subject.subject_name}) เรียบร้อยแล้ว")
            return redirect("subject_list")
        else:
            messages.error(request, "กรุณาตรวจสอบข้อมูลที่กรอกอีกครั้ง")
    else:
        form = SubjectForm()
    
    context = {
        "title": "เพิ่มรายวิชาใหม่ (Add Subject)",
        "form": form,
        "action": "create",
        "date": datetime.datetime.today(),
    }
    return render(request, "subject_form.html", context)


@login_required
def subject_update(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == "POST":
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            subject = form.save()
            messages.success(request, f"แก้ไขรายวิชา {subject.subject_code} เรียบร้อยแล้ว")
            return redirect("subject_detail", pk=subject.pk)
        else:
            messages.error(request, "กรุณาตรวจสอบข้อมูลที่กรอกอีกครั้ง")
    else:
        form = SubjectForm(instance=subject)
    
    context = {
        "title": f"แก้ไขรายวิชา: {subject.subject_code} - {subject.subject_name}",
        "form": form,
        "subject": subject,
        "action": "update",
        "date": datetime.datetime.today(),
    }
    return render(request, "subject_form.html", context)


@login_required
def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == "POST":
        code = subject.subject_code
        subject.delete()
        messages.success(request, f"ลบรายวิชา {code} เรียบร้อยแล้ว")
        return redirect("subject_list")
    
    context = {
        "title": f"ยืนยันการลบรายวิชา: {subject.subject_code}",
        "subject": subject,
        "date": datetime.datetime.today(),
    }
    return render(request, "subject_confirm_delete.html", context)


# ---------------- Authentication ----------------
def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"ยินดีต้อนรับคุณ {user.username} เข้าสู่ระบบสำเร็จ")
                next_url = request.GET.get("next")
                if next_url:
                    return redirect(next_url)
                return redirect("home")
            else:
                messages.error(request, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
        else:
            messages.error(request, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง")
    else:
        form = AuthenticationForm()

    context = {
        "title": "เข้าสู่ระบบ (Login)",
        "form": form,
        "date": datetime.datetime.today(),
    }
    return render(request, "login.html", context)


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get("password"))
            user.save()
            # Log in automatically after registration
            login(request, user)
            messages.success(request, f"ยินดีต้อนรับคุณ {user.username} สมัครสมาชิกและเข้าสู่ระบบเรียบร้อยแล้ว")
            return redirect("home")
        else:
            messages.error(request, "กรุณาตรวจสอบข้อมูลการสมัครสมาชิกอีกครั้ง")
    else:
        form = RegisterForm()

    context = {
        "title": "สมัครสมาชิก (Register)",
        "form": form,
        "date": datetime.datetime.today(),
    }
    return render(request, "register.html", context)


def social_login_view(request, provider):
    if provider == "google":
        username = "google_user"
        email = "user@gmail.com"
        first_name = "Google"
        last_name = "Account"
        provider_name = "Google Account"
    elif provider == "line":
        username = "line_user"
        email = "user@line.me"
        first_name = "LINE"
        last_name = "Account"
        provider_name = "LINE"
    else:
        messages.error(request, "ไม่พบผู้ให้บริการล็อกอินนี้")
        return redirect("login")

    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
        }
    )
    login(request, user)
    if created:
        messages.success(request, f"สมัครสมาชิกและเข้าสู่ระบบด้วย {provider_name} สำเร็จ")
    else:
        messages.success(request, f"เข้าสู่ระบบด้วย {provider_name} สำเร็จ")

    return redirect("home")


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "ออกจากระบบเรียบร้อยแล้ว")
    return redirect("login")