from django.core.management.base import BaseCommand
from django.utils.text import slugify
from store.models import Product

SAMPLES = [
    ("Everyday Backpack", "A durable, lightweight backpack with room for daily essentials.", "1299.00", "Accessories", 18, "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=900"),
    ("Wireless Headphones", "Comfortable over-ear headphones for music, study and travel.", "2499.00", "Electronics", 12, "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=900"),
    ("Classic Wristwatch", "A clean, timeless design that works from weekdays to weekends.", "1899.00", "Accessories", 9, "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=900"),
    ("Ceramic Coffee Mug", "A minimal ceramic mug for your morning coffee or evening tea.", "399.00", "Home", 30, "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?w=900"),
    ("Running Sneakers", "Versatile everyday sneakers with a cushioned, comfortable fit.", "2199.00", "Fashion", 15, "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=900"),
    ("Desk Lamp", "A modern desk lamp to brighten your workspace.", "999.00", "Home", 14, "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=900"),
]
class Command(BaseCommand):
    help = "Create a few sample products for the store."
    def handle(self, *args, **options):
        for name, description, price, category, stock, image_url in SAMPLES:
            slug = slugify(name)
            Product.objects.update_or_create(slug=slug, defaults={
                "name": name, "description": description, "price": price,
                "category": category, "stock": stock, "image_url": image_url, "is_active": True
            })
        self.stdout.write(self.style.SUCCESS("Sample products created/updated."))
