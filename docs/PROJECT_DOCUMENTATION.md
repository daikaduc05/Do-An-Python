# 📚 Tài Liệu Dự Án: Website Bán Sách Online

## Mục Lục
1. [Giới Thiệu](#giới-thiệu)
2. [Công Nghệ Sử Dụng](#công-nghệ-sử-dụng)
3. [Cấu Trúc Dự Án](#cấu-trúc-dự-án)
4. [Các Tính Năng Chính](#các-tính-năng-chính)
5. [Database Schema](#database-schema)
6. [API Endpoints](#api-endpoints)
7. [Hướng Dẫn Cài Đặt](#hướng-dẫn-cài-đặt)
8. [Tích Hợp AI](#tích-hợp-ai)

---

## Giới Thiệu

Dự án xây dựng một website bán sách online với các tính năng cơ bản như đăng nhập/đăng ký, quản lý giỏ hàng, phân loại sách theo danh mục, và **đề xuất sách thông minh bằng AI**.

### Mục Tiêu
- Tạo trải nghiệm mua sách trực tuyến tiện lợi
- Hệ thống đề xuất sách cá nhân hóa dựa trên AI
- Giao diện thân thiện, dễ sử dụng

---

## Công Nghệ Sử Dụng

| Công Nghệ | Phiên Bản | Mô Tả |
|-----------|-----------|-------|
| **Python** | 3.10+ | Ngôn ngữ lập trình chính |
| **Django** | 4.2+ | Web Framework |
| **Django REST Framework** | 3.14+ | Xây dựng REST API |
| **PostgreSQL** | 14+ | Cơ sở dữ liệu |
| **Redis** | 7.0+ | Cache & Session |
| **Celery** | 5.3+ | Task Queue (cho AI processing) |
| **OpenAI API / Google AI** | Latest | Đề xuất sách bằng AI |

---

## Cấu Trúc Dự Án

```
bookstore/
├── manage.py
├── requirements.txt
├── .env                      # Environment variables
│
├── bookstore/                # Project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/
│   ├── accounts/             # Xác thực người dùng
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── forms.py
│   │
│   ├── books/                # Quản lý sách
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── admin.py
│   │
│   ├── categories/           # Danh mục sách
│   │   ├── models.py
│   │   ├── views.py
│   │   └── urls.py
│   │
│   ├── cart/                 # Giỏ hàng
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── urls.py
│   │
│   ├── orders/               # Đơn hàng
│   │   ├── models.py
│   │   ├── views.py
│   │   └── urls.py
│   │
│   └── ai_recommendations/   # Đề xuất AI
│       ├── services.py
│       ├── views.py
│       └── urls.py
│
├── templates/                # HTML Templates
│   ├── base.html
│   ├── accounts/
│   ├── books/
│   └── cart/
│
└── static/                   # Static files
    ├── css/
    ├── js/
    └── images/
```

---

## Các Tính Năng Chính

### 1. 🔐 Hệ Thống Đăng Nhập/Đăng Ký

**Chức năng:**
- Đăng ký tài khoản mới
- Đăng nhập/Đăng xuất
- Quên mật khẩu
- Xác thực email
- Quản lý profile người dùng

**Model User (accounts/models.py):**
```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email
```

### 2. 📂 Danh Mục Sách (Categories)

**Chức năng:**
- Hiển thị danh sách danh mục
- Lọc sách theo danh mục
- Danh mục cha/con (nested categories)

**Model Category (categories/models.py):**
```python
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children'
    )
    image = models.ImageField(upload_to='categories/', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
```

### 3. 📖 Quản Lý Sách (Books)

**Chức năng:**
- CRUD sách (Admin)
- Hiển thị danh sách sách
- Chi tiết sách
- Tìm kiếm sách
- Lọc theo giá, tác giả, nhà xuất bản

**Model Book (books/models.py):**
```python
from django.db import models
from apps.categories.models import Category

class Author(models.Model):
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='authors/', blank=True)
    
    def __str__(self):
        return self.name

class Publisher(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=500)
    slug = models.SlugField(unique=True)
    isbn = models.CharField(max_length=13, unique=True)
    description = models.TextField()
    
    # Relationships
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, related_name='books')
    categories = models.ManyToManyField(Category, related_name='books')
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Inventory
    stock = models.PositiveIntegerField(default=0)
    
    # Media
    cover_image = models.ImageField(upload_to='books/covers/')
    
    # Metadata
    publication_date = models.DateField()
    pages = models.PositiveIntegerField()
    language = models.CharField(max_length=50, default='Vietnamese')
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def final_price(self):
        return self.discount_price if self.discount_price else self.price

class BookReview(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['book', 'user']
```

### 4. 🛒 Giỏ Hàng (Shopping Cart)

**Chức năng:**
- Thêm sách vào giỏ
- Cập nhật số lượng
- Xóa sách khỏi giỏ
- Tính tổng tiền
- Lưu giỏ hàng (session hoặc database)

**Model Cart (cart/models.py):**
```python
from django.db import models
from apps.accounts.models import CustomUser
from apps.books.models import Book

class Cart(models.Model):
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='cart',
        null=True, 
        blank=True
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart {self.id}"
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['cart', 'book']
    
    @property
    def subtotal(self):
        return self.book.final_price * self.quantity
```

### 5. 🤖 Đề Xuất Sách Bằng AI

**Chức năng:**
- Đề xuất sách dựa trên lịch sử mua hàng
- Đề xuất sách tương tự
- Chat với AI để tìm sách phù hợp
- Đề xuất dựa trên sở thích người dùng

**Service AI (ai_recommendations/services.py):**
```python
import openai
from django.conf import settings
from apps.books.models import Book

class AIRecommendationService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
    
    def get_recommendations_by_history(self, user):
        """Đề xuất sách dựa trên lịch sử mua hàng"""
        # Lấy lịch sử mua hàng
        purchased_books = user.orders.values_list('items__book__title', flat=True)
        
        if not purchased_books:
            return self.get_popular_books()
        
        prompt = f"""
        Dựa trên các sách đã mua sau đây:
        {', '.join(purchased_books)}
        
        Hãy đề xuất 5 cuốn sách tương tự mà người dùng có thể thích.
        Trả về dạng JSON với các trường: title, author, reason
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Bạn là một chuyên gia về sách."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content
    
    def get_similar_books(self, book):
        """Đề xuất sách tương tự"""
        prompt = f"""
        Đề xuất 5 cuốn sách tương tự với:
        Tên sách: {book.title}
        Tác giả: {book.author.name}
        Thể loại: {', '.join(book.categories.values_list('name', flat=True))}
        Mô tả: {book.description[:500]}
        
        Trả về dạng JSON array với các trường: title, author, similarity_reason
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Bạn là một chuyên gia về sách."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content
    
    def chat_recommendation(self, user_message, user_preferences=None):
        """Chat với AI để tìm sách phù hợp"""
        system_prompt = """
        Bạn là trợ lý tư vấn sách thông minh. 
        Nhiệm vụ của bạn là:
        1. Hiểu nhu cầu đọc sách của người dùng
        2. Đề xuất những cuốn sách phù hợp
        3. Giải thích lý do tại sao sách đó phù hợp
        
        Hãy trả lời bằng tiếng Việt, thân thiện và hữu ích.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    def get_popular_books(self, limit=10):
        """Lấy sách phổ biến khi không có lịch sử"""
        return Book.objects.filter(
            is_active=True
        ).order_by('-created_at')[:limit]
```

**View AI (ai_recommendations/views.py):**
```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .services import AIRecommendationService

class AIRecommendationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def __init__(self):
        super().__init__()
        self.ai_service = AIRecommendationService()
    
    def get(self, request):
        """Lấy đề xuất sách dựa trên lịch sử"""
        recommendations = self.ai_service.get_recommendations_by_history(request.user)
        return Response({'recommendations': recommendations})
    
    def post(self, request):
        """Chat với AI để tìm sách"""
        user_message = request.data.get('message', '')
        
        if not user_message:
            return Response({'error': 'Message is required'}, status=400)
        
        response = self.ai_service.chat_recommendation(user_message)
        return Response({'response': response})

class SimilarBooksView(APIView):
    def get(self, request, book_id):
        """Lấy sách tương tự"""
        from apps.books.models import Book
        
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=404)
        
        ai_service = AIRecommendationService()
        similar_books = ai_service.get_similar_books(book)
        
        return Response({'similar_books': similar_books})
```

---

## Database Schema

### ERD (Entity Relationship Diagram)

```
┌─────────────────┐      ┌─────────────────┐       ┌─────────────────┐
│   CustomUser    │      │     Category    │       │     Author      │
├─────────────────┤      ├─────────────────┤       ├─────────────────┤
│ id              │      │ id              │       │ id              │
│ username        │      │ name            │       │ name            │
│ email           │      │ slug            │       │ bio             │
│ password        │      │ description     │       │ image           │
│ phone           │      │ parent_id (FK)  │       └────────┬────────┘
│ address         │      │ image           │                │
│ avatar          │      │ is_active       │                │
└────────┬────────┘      └────────┬────────┘                │
         │                        │                          │
         │                        │ M:N                      │ 1:N
         │                        ▼                          ▼
         │               ┌─────────────────┐       ┌─────────────────┐
         │               │      Book       │◄──────│   Publisher     │
         │               ├─────────────────┤       ├─────────────────┤
         │               │ id              │       │ id              │
         │               │ title           │       │ name            │
         │      1:N      │ isbn            │       │ address         │
         │    ┌──────────│ author_id (FK)  │       └─────────────────┘
         │    │          │ publisher_id(FK)│
         │    │          │ price           │
         │    │          │ stock           │
         │    │          │ cover_image     │
         │    │          └────────┬────────┘
         │    │                   │
         │    │                   │ 1:N
         │    ▼                   ▼
┌────────┴────────┐      ┌─────────────────┐
│      Cart       │      │   BookReview    │
├─────────────────┤      ├─────────────────┤
│ id              │      │ id              │
│ user_id (FK)    │      │ book_id (FK)    │
│ session_key     │      │ user_id (FK)    │
│ created_at      │      │ rating          │
└────────┬────────┘      │ comment         │
         │               └─────────────────┘
         │ 1:N
         ▼
┌─────────────────┐      ┌─────────────────┐
│    CartItem     │      │     Order       │
├─────────────────┤      ├─────────────────┤
│ id              │      │ id              │
│ cart_id (FK)    │      │ user_id (FK)    │
│ book_id (FK)    │      │ total_amount    │
│ quantity        │      │ status          │
└─────────────────┘      │ shipping_address│
                         │ payment_method  │
                         └────────┬────────┘
                                  │ 1:N
                                  ▼
                         ┌─────────────────┐
                         │   OrderItem     │
                         ├─────────────────┤
                         │ id              │
                         │ order_id (FK)   │
                         │ book_id (FK)    │
                         │ quantity        │
                         │ price           │
                         └─────────────────┘
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Mô Tả |
|--------|----------|-------|
| POST | `/api/auth/register/` | Đăng ký tài khoản |
| POST | `/api/auth/login/` | Đăng nhập |
| POST | `/api/auth/logout/` | Đăng xuất |
| POST | `/api/auth/password/reset/` | Quên mật khẩu |
| GET/PUT | `/api/auth/profile/` | Xem/Cập nhật profile |

### Books

| Method | Endpoint | Mô Tả |
|--------|----------|-------|
| GET | `/api/books/` | Danh sách sách |
| GET | `/api/books/{id}/` | Chi tiết sách |
| GET | `/api/books/search/?q=keyword` | Tìm kiếm sách |
| GET | `/api/books/featured/` | Sách nổi bật |

### Categories

| Method | Endpoint | Mô Tả |
|--------|----------|-------|
| GET | `/api/categories/` | Danh sách danh mục |
| GET | `/api/categories/{slug}/books/` | Sách theo danh mục |

### Cart

| Method | Endpoint | Mô Tả |
|--------|----------|-------|
| GET | `/api/cart/` | Xem giỏ hàng |
| POST | `/api/cart/add/` | Thêm vào giỏ |
| PUT | `/api/cart/update/{item_id}/` | Cập nhật số lượng |
| DELETE | `/api/cart/remove/{item_id}/` | Xóa khỏi giỏ |
| DELETE | `/api/cart/clear/` | Xóa toàn bộ giỏ |

### AI Recommendations

| Method | Endpoint | Mô Tả |
|--------|----------|-------|
| GET | `/api/ai/recommendations/` | Đề xuất sách cho user |
| POST | `/api/ai/chat/` | Chat với AI tìm sách |
| GET | `/api/ai/similar/{book_id}/` | Sách tương tự |

---

## Hướng Dẫn Cài Đặt

### 1. Clone và Setup Environment

```bash
# Clone repository
git clone <repository-url>
cd bookstore

# Tạo virtual environment
python -m venv venv

# Kích hoạt (Windows)
venv\Scripts\activate

# Kích hoạt (Linux/Mac)
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

### 2. File requirements.txt

```txt
Django==4.2.7
djangorestframework==3.14.0
django-cors-headers==4.3.0
Pillow==10.1.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
openai==0.28.0
celery==5.3.4
redis==5.0.1
django-redis==5.4.0
gunicorn==21.2.0
whitenoise==6.6.0
```

### 3. Cấu hình .env

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgres://user:password@localhost:5432/bookstore

# Redis (for caching & Celery)
REDIS_URL=redis://localhost:6379/0

# OpenAI API
OPENAI_API_KEY=sk-your-openai-api-key

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 4. Database Migration

```bash
# Tạo migrations
python manage.py makemigrations accounts books categories cart orders ai_recommendations

# Apply migrations
python manage.py migrate

# Tạo superuser
python manage.py createsuperuser

# Load sample data (nếu có)
python manage.py loaddata fixtures/sample_data.json
```

### 5. Chạy Development Server

```bash
# Chạy Django server
python manage.py runserver

# Chạy Celery worker (terminal khác)
celery -A bookstore worker -l info
```

---

## Tích Hợp AI

### Các Provider AI Có Thể Sử Dụng

1. **OpenAI (ChatGPT)**
   - Ưu điểm: Mạnh mẽ, hiểu ngữ cảnh tốt
   - Nhược điểm: Tốn phí

2. **Google AI (Gemini)**
   - Ưu điểm: Multimodal, giá tốt
   - Nhược điểm: Cần Google Cloud setup

3. **Hugging Face** (Open Source)
   - Ưu điểm: Miễn phí, tự host được
   - Nhược điểm: Cần GPU để chạy tốt

### Luồng Hoạt Động AI Recommendation

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   User      │────▶│  Django View    │────▶│  AI Service     │
│  Request    │     │                 │     │                 │
└─────────────┘     └─────────────────┘     └────────┬────────┘
                                                      │
                           ┌──────────────────────────┘
                           ▼
                    ┌─────────────────┐
                    │  OpenAI API     │
                    │  (hoặc AI khác) │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐     ┌─────────────────┐
                    │  AI Response    │────▶│  Match với DB   │
                    │  (JSON)         │     │  Books          │
                    └─────────────────┘     └────────┬────────┘
                                                      │
                           ┌──────────────────────────┘
                           ▼
                    ┌─────────────────┐
                    │  Return to User │
                    │  (Recommended   │
                    │   Books)        │
                    └─────────────────┘
```

---

## Timeline Phát Triển Dự Kiến

| Tuần | Công Việc |
|------|-----------|
| 1 | Setup project, models, database |
| 2 | Authentication (đăng nhập/đăng ký) |
| 3 | Books & Categories CRUD |
| 4 | Shopping Cart |
| 5 | Orders & Checkout |
| 6 | AI Recommendations Integration |
| 7 | Frontend UI/UX |
| 8 | Testing & Deployment |

---

## Tài Liệu Tham Khảo

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

*Tài liệu được tạo ngày: 19/01/2026*
*Phiên bản: 1.0*
