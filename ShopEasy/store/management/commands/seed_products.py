import shutil

from django.conf import settings
from django.core.management.base import BaseCommand

from store.models import Product

PRODUCTS = [
    ("tshirt", "T-shirt", "Soft 100% cotton crew-neck t-shirt. Comfortable for everyday wear.", 499, 25),
    ("headphones", "Headphones", "Over-ear wired headphones with deep bass and a padded headband.", 999, 15),
    ("watch", "Watch", "Classic analog watch with a stainless steel strap and water resistance.", 799, 20),
    ("shoes", "Shoes", "Lightweight running shoes with a cushioned sole and breathable mesh.", 1499, 12),
    ("backpack", "Backpack", "Roomy 25-litre backpack with a laptop sleeve and water-bottle pockets.", 1199, 18),
    ("sunglasses", "Sunglasses", "UV-protected sunglasses with a lightweight frame.", 699, 30),
]


class Command(BaseCommand):
    help = "Add sample products (with images) to the database."

    def handle(self, *args, **options):
        media_dir = settings.MEDIA_ROOT / "products"
        media_dir.mkdir(parents=True, exist_ok=True)
        created = 0
        for slug, name, description, price, stock in PRODUCTS:
            source = settings.BASE_DIR / "static" / "images" / f"{slug}.svg"
            if source.exists():
                shutil.copy(source, media_dir / f"{slug}.svg")
            _, was_created = Product.objects.get_or_create(
                name=name,
                defaults={
                    "description": description,
                    "price": price,
                    "stock": stock,
                    "image": f"products/{slug}.svg",
                },
            )
            created += was_created
        self.stdout.write(self.style.SUCCESS(f"Done. {created} new product(s) added."))
