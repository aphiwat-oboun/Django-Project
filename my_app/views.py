# pyrefly: ignore [missing-import]
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
import datetime
from .models import Student, Major
from .forms import StudentForm

def home(request):
    context = {
        "title": "รายชื่อนักศึกษา (Student List)",
    }
    
    context["students"] = Student.objects.all().order_by("id")
    context["majors"] = Major.objects.all().order_by("id")
    context["date"] = datetime.datetime.today()
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


def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)

    context = {
        "title": f"ข้อมูลนักศึกษา: {student.get_prefix_name_display()}{student.fname} {student.lname}",
        "student": student,
        "date": datetime.datetime.today(),
    }

    return render(request, "student_detail.html", context)


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


def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            student = form.save()
            messages.success(request, f"แก้ไขข้อมูลนักศึกษา {student.fname} {student.lname} สำเร็จแล้ว")
            return redirect("student_detail", pk=student.pk)
        else:
            messages.error(request, "กรุณาตรวจสอบข้อมูลที่กรอกอีกครั้ง")
    else:
        form = StudentForm(instance=student)
    
    context = {
        "title": f"แก้ไขข้อมูลนักศึกษา: {student.get_prefix_name_display()}{student.fname} {student.lname}",
        "form": form,
        "student": student,
        "action": "update",
        "date": datetime.datetime.today(),
    }
    return render(request, "student_form.html", context)


def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        student_name = f"{student.get_prefix_name_display()}{student.fname} {student.lname}"
        student.delete()
        messages.success(request, f"ลบข้อมูลนักศึกษา {student_name} เรียบร้อยแล้ว")
        return redirect("home")
    
    context = {
        "title": f"ยืนยันการลบข้อมูล: {student.get_prefix_name_display()}{student.fname} {student.lname}",
        "student": student,
        "date": datetime.datetime.today(),
    }
    return render(request, "student_confirm_delete.html", context)