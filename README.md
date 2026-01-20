# 📚 Ebook Store

> Website bán Ebook với tiền ảo (Coins) & AI đề xuất sách bằng **RAG + pgvector**

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-336791.svg)

## ✨ Tính Năng

- 🔐 Đăng ký / Đăng nhập
- 💰 Nạp tiền (Coins) vào tài khoản
- 📖 Mua & tải Ebook
- 🤖 **AI đề xuất sách với RAG + pgvector**

## 🗄️ Database (4 Bảng)

| Bảng | Mô Tả |
|------|-------|
| **User** | Người dùng + balance (Coins) |
| **Author** | Tác giả |
| **Ebook** | Sách + file_url + **embedding** (vector 1536d) |
| **Transaction** | Nạp tiền / Mua sách |

## 🤖 RAG Flow

```
User hỏi → Embed query → pgvector search → Top K ebooks → LLM + context → Response
```

## 🚀 Quick Start

```bash
# Setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Enable pgvector
psql ebook_store -c "CREATE EXTENSION vector;"

# Migrate & Run
python manage.py migrate
python manage.py runserver
```

## 📖 Tài Liệu Chi Tiết

[📄 PROJECT_DOCUMENTATION.md](./docs/PROJECT_DOCUMENTATION.md)
