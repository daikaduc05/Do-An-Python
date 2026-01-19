# 📚 BookStore - Website Bán Sách Online

> **Dự án Django** - Website bán sách với tính năng đề xuất sách thông minh bằng AI

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2+-green.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-API-orange.svg)

## ✨ Tính Năng Chính

| Tính Năng | Mô Tả |
|-----------|-------|
| 🔐 **Authentication** | Đăng ký, đăng nhập, quản lý tài khoản |
| 📂 **Categories** | Phân loại sách theo danh mục |
| 📖 **Books** | Xem, tìm kiếm, lọc sách |
| 🛒 **Shopping Cart** | Giỏ hàng với đầy đủ chức năng |
| 🤖 **AI Recommendations** | Đề xuất sách thông minh bằng AI |

## 🚀 Quick Start

```bash
# 1. Clone project
git clone <repo-url>
cd bookstore

# 2. Tạo virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# 3. Cài đặt dependencies
pip install -r requirements.txt

# 4. Setup database
python manage.py migrate
python manage.py createsuperuser

# 5. Chạy server
python manage.py runserver
```

## 📁 Cấu Trúc Dự Án

```
bookstore/
├── apps/
│   ├── accounts/          # 🔐 User authentication
│   ├── books/             # 📖 Book management
│   ├── categories/        # 📂 Categories
│   ├── cart/              # 🛒 Shopping cart
│   ├── orders/            # 📦 Orders
│   └── ai_recommendations/# 🤖 AI features
├── templates/
├── static/
└── docs/
```

## 📖 Tài Liệu

Xem chi tiết tại: [📄 PROJECT_DOCUMENTATION.md](./docs/PROJECT_DOCUMENTATION.md)

## 🛠️ Tech Stack

- **Backend**: Django 4.2, Django REST Framework
- **Database**: PostgreSQL
- **Cache**: Redis
- **AI**: OpenAI API / Google AI
- **Task Queue**: Celery

## 👥 Team

*Đồ án Python*

---

⭐ **Star** repo này nếu bạn thấy hữu ích!
