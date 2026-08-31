from django import forms
from django.contrib.auth.models import User
from .models import Student, Subject, Enrolls

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


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['subject_code', 'subject_name', 'category']
        labels = {
            'subject_code': 'รหัสวิชา',
            'subject_name': 'ชื่อรายวิชา',
            'category': 'หมวดหมู่วิชา',
        }
        widgets = {
            'subject_code': forms.TextInput(attrs={
                'class': 'form-control font-monospace',
                'placeholder': 'เช่น CS101, CS201',
            }),
            'subject_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'เช่น พื้นฐานวิทยาการคอมพิวเตอร์',
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
        }


class EnrollsForm(forms.ModelForm):
    class Meta:
        model = Enrolls
        fields = ['subject', 'semester']
        labels = {
            'subject': 'เลือกรายวิชาเรียน',
            'semester': 'เลือกภาคเรียน',
        }
        widgets = {
            'subject': forms.Select(attrs={
                'class': 'form-select',
            }),
            'semester': forms.Select(attrs={
                'class': 'form-select',
            }),
        }


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label="รหัสผ่าน",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'กำหนดรหัสผ่าน'})
    )
    confirm_password = forms.CharField(
        label="ยืนยันรหัสผ่าน",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'ยืนยันรหัสผ่าน'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': 'ชื่อผู้ใช้งาน (Username)',
            'email': 'อีเมล (Email)',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'เช่น student_dev'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@university.ac.th'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("ชื่อผู้ใช้นี้มีอยู่ในระบบแล้ว กรุณาเลือกชื่ออื่น")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "รหัสผ่านทั้งสองช่องไม่ตรงกัน")

        return cleaned_data
