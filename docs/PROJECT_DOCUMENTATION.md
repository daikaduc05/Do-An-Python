# 📚 Tài Liệu Dự Án: Website Bán Ebook Online

## Mục Lục
1. [Giới Thiệu](#giới-thiệu)
2. [Công Nghệ Sử Dụng](#công-nghệ-sử-dụng)
3. [Cấu Trúc Dự Án](#cấu-trúc-dự-án)
4. [Các Tính Năng Chính](#các-tính-năng-chính)
5. [Database Schema](#database-schema)
6. [API Endpoints](#api-endpoints)
7. [Hướng Dẫn Cài Đặt](#hướng-dẫn-cài-đặt)
8. [Tích Hợp AI với RAG](#tích-hợp-ai-với-rag)

---

## Giới Thiệu

Dự án xây dựng một website **bán Ebook online** với hệ thống **tiền ảo (Coins)** để nạp tiền và mua sách. Tích hợp **AI đề xuất sách sử dụng RAG (Retrieval Augmented Generation)** với **pgvector**.

### Mục Tiêu
- 📖 Mua ebook trực tiếp bằng tiền ảo (Coins)
- 💰 Nạp tiền → Mua sách → Tải file
- 🤖 AI đề xuất sách sử dụng **RAG + PostgreSQL pgvector**

---

## Công Nghệ Sử Dụng

| Công Nghệ | Phiên Bản | Mô Tả |
|-----------|-----------|-------|
| **Python** | 3.10+ | Ngôn ngữ lập trình chính |
| **Django** | 4.2+ | Web Framework |
| **Django REST Framework** | 3.14+ | Xây dựng REST API |
| **PostgreSQL** | 14+ | Cơ sở dữ liệu |
| **pgvector** | 0.5+ | Vector similarity search cho RAG |
| **OpenAI API** | Latest | Embeddings + Chat Completion |

---

## Cấu Trúc Dự Án

```
ebook_store/
├── manage.py
├── requirements.txt
├── .env
│
├── ebook_store/              # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── apps/
│   ├── accounts/             # User & Authentication
│   │   ├── models.py
│   │   ├── views.py
│   │   └── urls.py
│   │
│   ├── ebooks/               # Ebook & Author
│   │   ├── models.py
│   │   ├── views.py
│   │   └── urls.py
│   │
│   ├── transactions/         # Nạp tiền & Mua sách
│   │   ├── models.py
│   │   ├── views.py
│   │   └── urls.py
│   │
│   └── ai_rag/               # 🤖 AI RAG với pgvector
│       ├── models.py         # EbookEmbedding
│       ├── services.py       # RAG Service
│       ├── views.py
│       └── urls.py
│
├── templates/
├── static/
└── media/
    └── ebooks/               # File ebook (PDF)
```

---

## Các Tính Năng Chính

### 1. 🔐 Đăng Nhập/Đăng Ký

- Đăng ký tài khoản
- Đăng nhập/Đăng xuất  
- Xem số dư Coins

### 2. 📖 Quản Lý Ebook

- Xem danh sách ebook
- Xem chi tiết ebook
- Tìm kiếm ebook
- Lọc theo tác giả, thể loại

### 3. 💰 Hệ Thống Tiền Ảo

- **Nạp tiền vào**: User nạp tiền → Cộng Coins
- **Tiêu tiền (mua sách)**: Mua ebook → Trừ Coins → Tải file

### 4. 🤖 AI Đề Xuất Sách (RAG + pgvector)

- Tìm kiếm semantic bằng vector similarity
- Chat với AI có context từ database sách
- Đề xuất sách chính xác dựa trên nội dung thực tế

---

## Database Schema

### 4 Bảng Chính + 1 Bảng Embedding

```
┌─────────────────────────────────────────────────────────────────┐
│                         DATABASE SCHEMA                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────┐          ┌─────────────────────┐
│        User         │          │       Author        │
├─────────────────────┤          ├─────────────────────┤
│ id (PK)             │          │ id (PK)             │
│ username            │          │ name                │
│ email               │          │ bio                 │
│ password            │          │ image               │
│ phone               │          │ created_at          │
│ avatar              │          └──────────┬──────────┘
│ balance (Coins) 💰  │                     │
│ created_at          │                     │ 1:N
│ updated_at          │                     │
└──────────┬──────────┘                     ▼
           │                     ┌─────────────────────┐
           │                     │       Ebook         │
           │                     ├─────────────────────┤
           │                     │ id (PK)             │
           │                     │ title               │
           │                     │ description         │
           │                     │ author_id (FK) ─────┼──► Author
           │                     │ category            │
           │                     │ price (Coins)       │
           │ 1:N                 │ file_url 📁         │
           │                     │ cover_image         │
           │                     │ embedding 🧠        │◄── Vector (1536 dimensions)
           │                     │ is_active           │
           │                     │ created_at          │
           │                     └─────────────────────┘
           │
           ▼
┌─────────────────────┐
│    Transaction      │
├─────────────────────┤
│ id (PK)             │
│ user_id (FK) ───────┼──► User
│ type                │    ('deposit' | 'purchase')
│ amount              │    (+ nạp vào, - mua sách)
│ ebook_id (FK)       │──► Ebook (nullable, chỉ khi mua)
│ description         │
│ balance_after       │
│ created_at          │
└─────────────────────┘
```

### Chi Tiết Các Bảng

#### 1. User (Người dùng)

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    balance = models.PositiveIntegerField(default=0)  # Số Coins hiện có
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def deposit(self, amount):
        """Nạp tiền vào tài khoản"""
        self.balance += amount
        self.save()
    
    def can_purchase(self, price):
        """Kiểm tra đủ tiền mua không"""
        return self.balance >= price
    
    def purchase(self, price):
        """Trừ tiền khi mua sách"""
        if self.can_purchase(price):
            self.balance -= price
            self.save()
            return True
        return False
```

#### 2. Author (Tác giả)

```python
class Author(models.Model):
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='authors/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
```

#### 3. Ebook (Sách điện tử) - Có Vector Embedding

```python
from pgvector.django import VectorField

class Ebook(models.Model):
    CATEGORY_CHOICES = [
        ('fiction', 'Tiểu thuyết'),
        ('science', 'Khoa học'),
        ('business', 'Kinh doanh'),
        ('self_help', 'Phát triển bản thân'),
        ('technology', 'Công nghệ'),
        ('history', 'Lịch sử'),
        ('children', 'Thiếu nhi'),
        ('other', 'Khác'),
    ]
    
    title = models.CharField(max_length=500)
    description = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='ebooks')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models.PositiveIntegerField(help_text="Giá bằng Coins")
    file_url = models.FileField(upload_to='ebooks/')
    cover_image = models.ImageField(upload_to='covers/')
    
    # 🧠 Vector embedding cho RAG (OpenAI text-embedding-3-small: 1536 dimensions)
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    def get_text_for_embedding(self):
        """Text để tạo embedding"""
        return f"{self.title}. {self.author.name}. {self.category}. {self.description}"
```

#### 4. Transaction (Giao dịch)

```python
class Transaction(models.Model):
    TYPE_CHOICES = [
        ('deposit', 'Nạp tiền'),      # + Coins
        ('purchase', 'Mua sách'),     # - Coins
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.IntegerField()  # + khi nạp, - khi mua
    ebook = models.ForeignKey(
        Ebook, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    description = models.CharField(max_length=500)
    balance_after = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
```

---

## Tích Hợp AI với RAG

### RAG là gì?

**RAG (Retrieval Augmented Generation)** = Tìm kiếm dữ liệu liên quan + Đưa vào AI để trả lời

```
┌──────────────────────────────────────────────────────────────────────┐
│                          RAG FLOW                                     │
└──────────────────────────────────────────────────────────────────────┘

   User Query                    Vector Search                  LLM Response
       │                              │                              │
       ▼                              ▼                              ▼
┌─────────────┐    Embed    ┌─────────────────┐   Context   ┌─────────────┐
│ "Tôi muốn   │ ─────────►  │   PostgreSQL    │ ─────────►  │   OpenAI    │
│  đọc sách   │   Query     │   + pgvector    │   Top K     │   GPT-4     │
│  về AI"     │   Vector    │                 │   Results   │             │
└─────────────┘             │  ┌───────────┐  │             │  Generate   │
                            │  │ Ebook 1   │  │             │  Response   │
                            │  │ Ebook 2   │  │             │  with       │
                            │  │ Ebook 3   │  │             │  Context    │
                            │  └───────────┘  │             └──────┬──────┘
                            └─────────────────┘                    │
                                                                   ▼
                                                          ┌─────────────┐
                                                          │ "Đây là 3   │
                                                          │  cuốn sách  │
                                                          │  về AI..."  │
                                                          └─────────────┘
```

### Setup pgvector trong PostgreSQL

```sql
-- Cài đặt extension pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Index cho tìm kiếm nhanh (HNSW - nhanh hơn IVFFlat)
CREATE INDEX ON ebooks_ebook 
USING hnsw (embedding vector_cosine_ops);
```

### RAG Service (ai_rag/services.py)

```python
import openai
from django.conf import settings
from pgvector.django import CosineDistance
from apps.ebooks.models import Ebook

class RAGService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.embedding_model = "text-embedding-3-small"  # 1536 dimensions
        self.chat_model = "gpt-3.5-turbo"
    
    def get_embedding(self, text):
        """Tạo embedding vector từ text"""
        response = openai.Embedding.create(
            model=self.embedding_model,
            input=text
        )
        return response['data'][0]['embedding']
    
    def search_similar_ebooks(self, query, top_k=5):
        """Tìm ebook tương tự bằng vector similarity"""
        # 1. Tạo embedding cho query
        query_embedding = self.get_embedding(query)
        
        # 2. Tìm kiếm trong PostgreSQL với pgvector
        similar_ebooks = Ebook.objects.filter(
            is_active=True,
            embedding__isnull=False
        ).annotate(
            distance=CosineDistance('embedding', query_embedding)
        ).order_by('distance')[:top_k]
        
        return similar_ebooks
    
    def build_context(self, ebooks):
        """Xây dựng context từ danh sách ebook"""
        context = "Dưới đây là danh sách sách có trong cửa hàng:\n\n"
        
        for i, ebook in enumerate(ebooks, 1):
            context += f"""
{i}. **{ebook.title}**
   - Tác giả: {ebook.author.name}
   - Thể loại: {ebook.get_category_display()}
   - Giá: {ebook.price} Coins
   - Mô tả: {ebook.description[:200]}...
"""
        return context
    
    def chat(self, user_message):
        """Chat với AI sử dụng RAG"""
        # 1. Tìm sách liên quan
        relevant_ebooks = self.search_similar_ebooks(user_message, top_k=5)
        
        # 2. Xây dựng context
        context = self.build_context(relevant_ebooks)
        
        # 3. Gọi LLM với context
        system_prompt = f"""Bạn là trợ lý tư vấn sách cho cửa hàng ebook.

{context}

Hãy dựa trên danh sách sách trên để tư vấn cho khách hàng.
- Chỉ đề xuất sách có trong danh sách
- Giải thích tại sao sách đó phù hợp
- Nếu không có sách phù hợp, hãy nói rõ
- Trả lời bằng tiếng Việt, thân thiện
"""
        
        response = openai.ChatCompletion.create(
            model=self.chat_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return {
            'response': response.choices[0].message.content,
            'relevant_ebooks': [
                {
                    'id': e.id,
                    'title': e.title,
                    'author': e.author.name,
                    'price': e.price,
                    'cover': e.cover_image.url if e.cover_image else None
                }
                for e in relevant_ebooks
            ]
        }
    
    def create_ebook_embedding(self, ebook):
        """Tạo embedding cho 1 ebook (gọi khi thêm/sửa sách)"""
        text = ebook.get_text_for_embedding()
        embedding = self.get_embedding(text)
        
        ebook.embedding = embedding
        ebook.save(update_fields=['embedding'])
        
        return True
    
    def update_all_embeddings(self):
        """Cập nhật embedding cho tất cả ebook (chạy 1 lần)"""
        ebooks = Ebook.objects.filter(is_active=True)
        
        for ebook in ebooks:
            self.create_ebook_embedding(ebook)
            print(f"Created embedding for: {ebook.title}")
        
        return len(ebooks)
```

### View AI RAG (ai_rag/views.py)

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .services import RAGService

class AIChatView(APIView):
    """Chat với AI sử dụng RAG"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        message = request.data.get('message', '')
        
        if not message:
            return Response({'error': 'Vui lòng nhập câu hỏi'}, status=400)
        
        rag_service = RAGService()
        result = rag_service.chat(message)
        
        return Response(result)


class SearchEbooksView(APIView):
    """Tìm kiếm semantic bằng vector"""
    
    def get(self, request):
        query = request.query_params.get('q', '')
        
        if not query:
            return Response({'error': 'Vui lòng nhập từ khóa'}, status=400)
        
        rag_service = RAGService()
        ebooks = rag_service.search_similar_ebooks(query, top_k=10)
        
        data = [{
            'id': e.id,
            'title': e.title,
            'author': e.author.name,
            'category': e.get_category_display(),
            'price': e.price,
            'cover': e.cover_image.url if e.cover_image else None,
            'similarity': 1 - e.distance  # Convert distance to similarity
        } for e in ebooks]
        
        return Response({'results': data})
```

### Django Signal - Tự động tạo Embedding

```python
# apps/ebooks/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Ebook
from apps.ai_rag.services import RAGService

@receiver(post_save, sender=Ebook)
def create_embedding_on_save(sender, instance, created, **kwargs):
    """Tự động tạo embedding khi thêm/sửa ebook"""
    if instance.is_active and not instance.embedding:
        rag_service = RAGService()
        rag_service.create_ebook_embedding(instance)
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Mô Tả |
|--------|----------|-------|
| POST | `/api/auth/register/` | Đăng ký |
| POST | `/api/auth/login/` | Đăng nhập |
| POST | `/api/auth/logout/` | Đăng xuất |
| GET | `/api/auth/profile/` | Xem profile & số dư |

### Ebooks

| Method | Endpoint | Mô Tả |
|--------|----------|-------|
| GET | `/api/ebooks/` | Danh sách ebook |
| GET | `/api/ebooks/{id}/` | Chi tiết ebook |
| GET | `/api/ebooks/category/{category}/` | Lọc theo thể loại |

### Transactions (Giao dịch)

| Method | Endpoint | Mô Tả |
|--------|----------|-------|
| POST | `/api/deposit/` | 💰 Nạp tiền |
| POST | `/api/ebooks/{id}/purchase/` | 🛒 Mua ebook |
| GET | `/api/my-ebooks/` | 📚 Ebook đã mua |
| GET | `/api/transactions/` | 📋 Lịch sử giao dịch |

### AI RAG

| Method | Endpoint | Mô Tả |
|--------|----------|-------|
| POST | `/api/ai/chat/` | 🤖 Chat với AI (RAG) |
| GET | `/api/ai/search/?q=keyword` | 🔍 Semantic search |

---

## Hướng Dẫn Cài Đặt

### 1. Cài đặt PostgreSQL + pgvector

```bash
# Ubuntu/Debian
sudo apt install postgresql-14-pgvector

# MacOS
brew install pgvector

# Windows: Dùng Docker
docker run -d --name postgres-vector \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  ankane/pgvector
```

### 2. Setup Django Project

```bash
# Clone
git clone <repo-url>
cd ebook_store

# Virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. requirements.txt

```txt
Django==4.2.7
djangorestframework==3.14.0
Pillow==10.1.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
openai==0.28.0
pgvector==0.2.4
```

### 4. .env

```env
SECRET_KEY=your-secret-key
DEBUG=True

# PostgreSQL with pgvector
DATABASE_URL=postgres://user:pass@localhost:5432/ebook_store

# OpenAI
OPENAI_API_KEY=sk-your-openai-key
```

### 5. settings.py - Cấu hình Database

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ebook_store',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 6. Migration

```bash
# Tạo database
createdb ebook_store

# Enable pgvector extension
psql ebook_store -c "CREATE EXTENSION vector;"

# Django migrate
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 7. Tạo Embedding cho Ebook có sẵn

```bash
python manage.py shell
```

```python
from apps.ai_rag.services import RAGService
rag = RAGService()
rag.update_all_embeddings()
```

### 8. Chạy Server

```bash
python manage.py runserver
```

---

## Ví Dụ Sử Dụng AI RAG

### Request

```bash
curl -X POST http://localhost:8000/api/ai/chat/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Tôi muốn tìm sách về lập trình Python cho người mới bắt đầu"}'
```

### Response

```json
{
  "response": "Dựa trên yêu cầu của bạn, tôi đề xuất các cuốn sách sau:\n\n1. **Python Crash Course** - Tác giả Eric Matthes\n   - Giá: 150 Coins\n   - Đây là cuốn sách rất phù hợp cho người mới bắt đầu...\n\n2. **Automate the Boring Stuff with Python**...",
  "relevant_ebooks": [
    {
      "id": 12,
      "title": "Python Crash Course",
      "author": "Eric Matthes",
      "price": 150,
      "cover": "/media/covers/python-crash-course.jpg"
    },
    {
      "id": 15,
      "title": "Automate the Boring Stuff with Python",
      "author": "Al Sweigart",
      "price": 120,
      "cover": "/media/covers/automate-python.jpg"
    }
  ]
}
```

---

## Tổng Kết

### 4 Bảng Database

| Bảng | Mô Tả |
|------|-------|
| **User** | Người dùng + balance (Coins) |
| **Author** | Tác giả |
| **Ebook** | Sách + file_url + **embedding** (vector) |
| **Transaction** | Nạp tiền / Mua sách |

### RAG Flow

```
User hỏi → Embed query → pgvector search → Top K ebooks → LLM + context → Response
```

### Ưu điểm RAG với pgvector

✅ Tìm kiếm semantic (hiểu ngữ nghĩa, không chỉ keyword)  
✅ AI trả lời dựa trên dữ liệu thực trong database  
✅ Không hallucinate (bịa sách không có)  
✅ Tìm kiếm nhanh với HNSW index  
✅ Dễ scale với PostgreSQL  

---

*Tài liệu được tạo ngày: 19/01/2026*
*Phiên bản: 4.0 - RAG + pgvector*
