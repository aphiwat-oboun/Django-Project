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
from django.urls import reverse
from django.conf import settings
import datetime
import requests
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

            # Allows enrolling subject repeatedly as requested
            enroll = form.save(commit=False)
            enroll.student = student
            enroll.save()
            messages.success(request, f"ลงทะเบียนวิชา {subject.subject_code} ({subject.subject_name}) ภาคเรียน {semester} สำเร็จ")
        else:
            messages.error(request, "กรุณาเลือกรายวิชาและภาคเรียนให้ถูกต้อง")

    return redirect("student_detail", pk=student.pk)


@login_required
def enroll_student_to_subject(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    if request.method == "POST":
        student_id = request.POST.get("student")
        semester = request.POST.get("semester")
        student = get_object_or_404(Student, pk=student_id)

        enroll = Enrolls.objects.create(
            student=student,
            subject=subject,
            semester=semester
        )
        messages.success(request, f"เพิ่มนักศึกษา {student.fname} {student.lname} ลงทะเบียนวิชา {subject.subject_code} ภาคเรียน {semester} สำเร็จ")

    return redirect("subject_detail", pk=subject.pk)


@login_required
def enroll_delete(request, pk):
    enroll = get_object_or_404(Enrolls.objects.select_related("student", "subject"), pk=pk)
    student_id = enroll.student.pk
    next_url = request.POST.get("next") or request.GET.get("next")
    subject_name = f"{enroll.subject.subject_code} - {enroll.subject.subject_name}"
    semester = enroll.semester
    enroll.delete()
    messages.success(request, f"ถอนการลงทะเบียนวิชา {subject_name} (ภาคเรียน {semester}) เรียบร้อยแล้ว")

    if next_url:
        return redirect(next_url)
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
    enrolls = subject.enrolls.select_related("student", "student__major").all().order_by("semester", "student__stu_id")
    all_students = Student.objects.select_related("major").all().order_by("stu_id")

    context = {
        "title": f"ข้อมูลรายวิชา: {subject.subject_code} - {subject.subject_name}",
        "subject": subject,
        "enrolls": enrolls,
        "all_students": all_students,
        "semesters": SEMESTER,
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


# ---------------- Authentication & Real OAuth 2.0 ----------------
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


# ---------------- Real OAuth 2.0 Social Login Flows ----------------
def social_login_view(request, provider):
    """
    Handles OAuth 2.0 redirection for Google, LINE, and GitHub.
    Uses credentials from .env.local if present, or provides clean simulation fallback.
    """
    provider = provider.lower()
    
    if provider == "google":
        client_id = getattr(settings, "GOOGLE_CLIENT_ID", "")
        if client_id:
            callback_uri = request.build_absolute_uri(reverse("social_callback", kwargs={"provider": "google"}))
            auth_url = (
                f"https://accounts.google.com/o/oauth2/v2/auth"
                f"?client_id={client_id}"
                f"&redirect_uri={callback_uri}"
                f"&response_type=code"
                f"&scope=openid%20email%20profile"
                f"&access_type=offline"
                f"&prompt=consent"
            )
            return redirect(auth_url)
        else:
            # Simulation fallback when API keys not yet filled in .env.local
            user, created = User.objects.get_or_create(
                username="google_user",
                defaults={"email": "google_student@university.ac.th", "first_name": "Google", "last_name": "Student"}
            )
            login(request, user)
            messages.success(request, "เข้าสู่ระบบด้วย Google Account สำเร็จ (กำหนด GOOGLE_CLIENT_ID ใน .env.local เพื่อใช้ Google จริง)")
            return redirect("home")

    elif provider == "line":
        channel_id = getattr(settings, "LINE_CHANNEL_ID", "")
        if channel_id:
            callback_uri = request.build_absolute_uri(reverse("social_callback", kwargs={"provider": "line"}))
            auth_url = (
                f"https://access.line.me/oauth2/v2.1/authorize"
                f"?response_type=code"
                f"&client_id={channel_id}"
                f"&redirect_uri={callback_uri}"
                f"&state=line_auth_state"
                f"&scope=profile%20openid%20email"
            )
            return redirect(auth_url)
        else:
            user, created = User.objects.get_or_create(
                username="line_user",
                defaults={"email": "line_student@line.me", "first_name": "LINE", "last_name": "User"}
            )
            login(request, user)
            messages.success(request, "เข้าสู่ระบบด้วย LINE สำเร็จ (กำหนด LINE_CHANNEL_ID ใน .env.local เพื่อใช้ LINE จริง)")
            return redirect("home")

    elif provider == "github":
        client_id = getattr(settings, "GITHUB_CLIENT_ID", "")
        if client_id:
            callback_uri = request.build_absolute_uri(reverse("social_callback", kwargs={"provider": "github"}))
            auth_url = (
                f"https://github.com/login/oauth/authorize"
                f"?client_id={client_id}"
                f"&redirect_uri={callback_uri}"
                f"&scope=user:email"
            )
            return redirect(auth_url)
        else:
            user, created = User.objects.get_or_create(
                username="github_user",
                defaults={"email": "developer@github.com", "first_name": "GitHub", "last_name": "Developer"}
            )
            login(request, user)
            messages.success(request, "เข้าสู่ระบบด้วย GitHub สำเร็จ (กำหนด GITHUB_CLIENT_ID ใน .env.local เพื่อใช้ GitHub จริง)")
            return redirect("home")

    else:
        messages.error(request, "ไม่พบผู้ให้บริการล็อกอินนี้")
        return redirect("login")


def social_callback_view(request, provider):
    """
    Handles OAuth 2.0 code exchange and user profile creation for Google, LINE, and GitHub.
    """
    provider = provider.lower()
    code = request.GET.get("code")
    error = request.GET.get("error")

    if error or not code:
        messages.error(request, f"การเข้าสู่ระบบด้วย {provider.capitalize()} ถูกยกเลิกหรือไม่สำเร็จ")
        return redirect("login")

    try:
        if provider == "google":
            client_id = getattr(settings, "GOOGLE_CLIENT_ID", "")
            client_secret = getattr(settings, "GOOGLE_CLIENT_SECRET", "")
            callback_uri = request.build_absolute_uri(reverse("social_callback", kwargs={"provider": "google"}))

            token_resp = requests.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": callback_uri,
                    "grant_type": "authorization_code",
                },
                timeout=10
            ).json()

            access_token = token_resp.get("access_token")
            if not access_token:
                messages.error(request, "ไม่สามารถรับ Token จาก Google ได้ กรุณาตรวจสอบ Client ID & Secret ใน .env.local")
                return redirect("login")

            user_info = requests.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10
            ).json()

            email = user_info.get("email", "")
            given_name = user_info.get("given_name", "")
            family_name = user_info.get("family_name", "")
            username = email.split("@")[0] if email else f"google_{user_info.get('sub', 'user')[:8]}"

            user, _ = User.objects.get_or_create(
                username=username,
                defaults={"email": email, "first_name": given_name, "last_name": family_name}
            )
            login(request, user)
            messages.success(request, f"ยินดีต้อนรับคุณ {user.first_name or user.username} เข้าสู่ระบบด้วย Google สำเร็จ")
            return redirect("home")

        elif provider == "github":
            client_id = getattr(settings, "GITHUB_CLIENT_ID", "")
            client_secret = getattr(settings, "GITHUB_CLIENT_SECRET", "")
            callback_uri = request.build_absolute_uri(reverse("social_callback", kwargs={"provider": "github"}))

            token_resp = requests.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": code,
                    "redirect_uri": callback_uri,
                },
                headers={"Accept": "application/json"},
                timeout=10
            ).json()

            access_token = token_resp.get("access_token")
            if not access_token:
                messages.error(request, "ไม่สามารถรับ Token จาก GitHub ได้ กรุณาตรวจสอบ Client ID & Secret ใน .env.local")
                return redirect("login")

            gh_user = requests.get(
                "https://api.github.com/user",
                headers={"Authorization": f"token {access_token}"},
                timeout=10
            ).json()

            gh_username = gh_user.get("login", "github_user")
            gh_name = gh_user.get("name", "") or gh_username
            gh_email = gh_user.get("email", "") or f"{gh_username}@github.user"

            user, _ = User.objects.get_or_create(
                username=gh_username,
                defaults={"email": gh_email, "first_name": gh_name}
            )
            login(request, user)
            messages.success(request, f"ยินดีต้อนรับคุณ {user.username} เข้าสู่ระบบด้วย GitHub สำเร็จ")
            return redirect("home")

        elif provider == "line":
            channel_id = getattr(settings, "LINE_CHANNEL_ID", "")
            channel_secret = getattr(settings, "LINE_CHANNEL_SECRET", "")
            callback_uri = request.build_absolute_uri(reverse("social_callback", kwargs={"provider": "line"}))

            token_resp = requests.post(
                "https://api.line.me/oauth2/v2.1/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": callback_uri,
                    "client_id": channel_id,
                    "client_secret": channel_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10
            ).json()

            access_token = token_resp.get("access_token")
            if not access_token:
                messages.error(request, "ไม่สามารถรับ Token จาก LINE ได้ กรุณาตรวจสอบ Channel ID & Secret ใน .env.local")
                return redirect("login")

            line_profile = requests.get(
                "https://api.line.me/v2/profile",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10
            ).json()

            line_user_id = line_profile.get("userId", "line_user")
            display_name = line_profile.get("displayName", "LINE User")
            username = f"line_{line_user_id[:8]}"

            user, _ = User.objects.get_or_create(
                username=username,
                defaults={"first_name": display_name, "email": f"{username}@line.me"}
            )
            login(request, user)
            messages.success(request, f"ยินดีต้อนรับคุณ {display_name} เข้าสู่ระบบด้วย LINE สำเร็จ")
            return redirect("home")

    except Exception as e:
        messages.error(request, f"เกิดข้อผิดพลาดในการเชื่อมต่อกับ {provider.capitalize()}: {str(e)}")
        return redirect("login")

    return redirect("home")


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "ออกจากระบบเรียบร้อยแล้ว")
    return redirect("login")