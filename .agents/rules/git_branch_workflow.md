# Git Branch Workflow Policy

## กฎการทำงานกับ Git Branch (สำคัญมาก)

- **ห้ามทำการเขียนโปรแกรมหรือแก้ไขโค้ดบน branch `main` โดยเด็ดขาด** (Strictly NEVER develop or commit on `main` branch).
- **ทุกการพัฒนา แก้ไขโค้ด และสร้างฟีเจอร์ใหม่ ต้องทำผ่าน branch `dev` เท่านั้น** (Always work on the `dev` branch).
- ตรวจสอบ branch ปัจจุบันเสมอ หากอยู่ที่ `main` ให้สลับไป `dev` ก่อนเริ่มทำงาน:
  ```bash
  git checkout dev
  ```
