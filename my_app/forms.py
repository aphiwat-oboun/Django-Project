from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['prefix_name', 'stu_id', 'fname', 'lname', 'major']
        labels = {
            'prefix_name': 'คำนำหน้าชื่อ',
            'stu_id': 'รหัสนักศึกษา',
            'fname': 'ชื่อ',
            'lname': 'นามสกุล',
            'major': 'สาขาวิชา',
        }
        widgets = {
            'prefix_name': forms.Select(attrs={
                'class': 'form-select',
            }),
            'stu_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'เช่น 6800000001',
            }),
            'fname': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'กรอกชื่อ',
            }),
            'lname': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'กรอกนามสกุล',
            }),
            'major': forms.Select(attrs={
                'class': 'form-select',
            }),
        }
