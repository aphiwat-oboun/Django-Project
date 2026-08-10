# pyrefly: ignore [missing-import]
from django.shortcuts import render, get_object_or_404
import datetime
from .models import Student, Major

def home(request):
    context = {
        "title": "My Home Page",
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
        "title": f"Student: {student.get_prefix_name_display()}{student.fname} {student.lname}",
        "student": student,
        "date": datetime.datetime.today(),
    }

    return render(request, "student_detail.html", context)

    