# Project Guidelines & Rules

## Git Branching Rules (Strict)

- **ห้ามแก้ไขโค้ดหรือเขียนโปรแกรมบน branch `main` โดยเด็ดขาด** (Never develop, edit code, or commit directly to the `main` branch).
- **การพัฒนาและการเขียนโค้ดทั้งหมดต้องทำผ่าน branch `dev` เท่านั้น** (All development and changes must be done on the `dev` branch).
- ก่อนเริ่มแก้ไขโค้ดหรือรันการเปลี่ยนแปลง ให้ตรวจสอบและมั่นใจว่าอยู่ใน branch `dev` เสมอ (`git branch` / `git checkout dev`).
