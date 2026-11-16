from django.core.management.base import BaseCommand

from products.models import Product


PRODUCTS = [
    {
        'name': 'Everyday Tote',
        'description': 'A durable canvas tote for work, errands, and weekends.',
        'price': '28.00',
        'stock': 24,
        'tax_percent': '8.25',
    },
    {
        'name': 'Stoneware Mug',
        'description': 'Hand-finished stoneware with a comfortable everyday handle.',
        'price': '18.00',
        'stock': 36,
        'tax_percent': '8.25',
    },
    {
        'name': 'Desk Lamp',
        'description': 'A warm, minimal lamp to make your workspace feel better.',
        'price': '64.00',
        'stock': 12,
        'tax_percent': '8.25',
    },
    {
        'name': 'Daily Notebook',
        'description': 'A lay-flat notebook for plans, lists, and good ideas.',
        'price': '14.00',
        'stock': 50,
        'tax_percent': '8.25',
    },
]


class Command(BaseCommand):
    help = 'Create or update the demo product catalog.'

    def handle(self, *args, **options):
        for product_data in PRODUCTS:
            Product.objects.update_or_create(
                name=product_data['name'],
                defaults={**product_data, 'is_active': True},
            )
        self.stdout.write(self.style.SUCCESS(f'Seeded {len(PRODUCTS)} products.'))
