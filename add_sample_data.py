import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ebook_store.settings')
django.setup()

from apps.ebooks.models import Author, Ebook

def add_sample_data():
    print("Starting to add sample data...")

    # 1. Create Authors
    authors_data = [
        {"name": "Robert C. Martin", "bio": "Uncle Bob, author of Clean Code."},
        {"name": "J.K. Rowling", "bio": "British author, best known for the Harry Potter series."},
        {"name": "Yuval Noah Harari", "bio": "Historian and philosopher."},
        {"name": "Paulo Coelho", "bio": "Brazilian lyricist and novelist."},
        {"name": "Nguyễn Nhật Ánh", "bio": "Nhà văn Việt Nam chuyên viết cho thanh thiếu niên."}
    ]

    authors = {}
    for data in authors_data:
        author, created = Author.objects.get_or_create(
            name=data["name"], 
            defaults={"bio": data["bio"]}
        )
        authors[data["name"]] = author
        if created:
            print(f"✅ Created author: {author.name}")
        else:
            print(f"ℹ️ Author exists: {author.name}")

    # 2. Create Ebooks
    ebooks_data = [
        {
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "category": "technology",
            "price": 300,
            "description": "A Handbook of Agile Software Craftsmanship. Even bad code can function. But if code isn't clean, it can bring a development organization to its knees."
        },
        {
            "title": "The Clean Coder",
            "author": "Robert C. Martin",
            "category": "technology",
            "price": 280,
            "description": "A Code of Conduct for Professional Programmers. Martin introduces the disciplines, techniques, tools, and practices of true software craftsmanship."
        },
        {
            "title": "Harry Potter and the Sorcerer's Stone",
            "author": "J.K. Rowling",
            "category": "fiction",
            "price": 150,
            "description": "Harry Potter has no idea how famous he is. That's because he's being raised by his miserable aunt and uncle who are terrified Harry will learn that he's really a wizard."
        },
        {
            "title": "Sapiens: A Brief History of Humankind",
            "author": "Yuval Noah Harari",
            "category": "science",
            "price": 200,
            "description": "From a renowned historian comes a groundbreaking narrative of humanity’s creation and evolution—a #1 international bestseller."
        },
        {
            "title": "Nhà Giả Kim (The Alchemist)",
            "author": "Paulo Coelho",
            "category": "fiction",
            "price": 120,
            "description": "Combining magic, mysticism, wisdom and wonder into an inspiring tale of self-discovery, The Alchemist has become a modern classic."
        },
        {
            "title": "Cho Tôi Xin Một Vé Đi Tuổi Thơ",
            "author": "Nguyễn Nhật Ánh",
            "category": "fiction",
            "price": 100,
            "description": "Truyện dài của Nguyễn Nhật Ánh, đưa người đọc trở về với thế giới hồn nhiên, tinh nghịch của trẻ thơ."
        },
        {
            "title": "Mắt Biếc",
            "author": "Nguyễn Nhật Ánh",
            "category": "fiction",
            "price": 110,
            "description": "Một câu chuyện tình yêu buồn và đẹp của Ngạn dành cho Hà Lan, được chuyển thể thành phim điện ảnh nổi tiếng."
        }
    ]

    for data in ebooks_data:
        author = authors.get(data["author"])
        if not author:
            print(f"⚠️ Skipping {data['title']} - Author not found")
            continue
            
        ebook, created = Ebook.objects.get_or_create(
            title=data["title"],
            defaults={
                "author": author,
                "category": data["category"],
                "price": data["price"],
                "description": data["description"]
            }
        )
        
        if created:
            print(f"✅ Created ebook: {ebook.title}")
            if ebook.embedding:
                print(f"   🧠 Embedding generated (dims: {len(ebook.embedding)})")
            else:
                print(f"   ⚠️ No embedding generated!")
        else:
            print(f"ℹ️ Ebook exists: {ebook.title}")

if __name__ == '__main__':
    add_sample_data()
