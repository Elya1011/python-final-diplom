import os, yaml
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from ...models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter

User = get_user_model()


class Command(BaseCommand):
    help = 'Загрузка тестовых данных из YAML файла в базу данных'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Путь к YAML файлу с данными')

    def handle(self, *args, **options):
        file_path = options['file_path']
        
        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f'Файл {file_path} не найден'))
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        with transaction.atomic():
            # Создаем или получаем пользователя по умолчанию для магазина
            user, created = User.objects.get_or_create(
                email='admin@example.com',
                defaults={
                    'is_active': True,
                    'is_staff': True,
                    'is_superuser': True,
                    'password': make_password('admin123'),
                    'type': 'shop'
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создан пользователь по умолчанию: {user.email}'))

            # Создаем или получаем магазин
            shop, _ = Shop.objects.get_or_create(
                name=data['shop'],
                defaults={
                    'url': None,
                    'user': user,
                    'state': True
                }
            )

            # Очищаем существующие данные магазина
            ProductInfo.objects.filter(shop=shop).delete()
            shop.categories.clear()

            # Создаем категории
            categories = {}
            for cat_data in data['categories']:
                category, _ = Category.objects.get_or_create(
                    id=cat_data['id'],
                    defaults={'name': cat_data['name']}
                )
                categories[cat_data['id']] = category
                shop.categories.add(category)

            # Обрабатываем товары
            for product_data in data['goods']:
                # Создаем или получаем продукт
                product, _ = Product.objects.get_or_create(
                    name=product_data['name'],
                    category=categories[product_data['category']]
                )

                # Создаем информацию о продукте
                product_info = ProductInfo.objects.create(
                    model=product_data.get('model', ''),
                    external_id=product_data['id'],
                    product=product,
                    shop=shop,
                    quantity=product_data['quantity'],
                    price=product_data['price'],
                    price_rrc=product_data.get('price_rrc', product_data['price'])
                )

                # Добавляем параметры продукта
                if 'parameters' in product_data and product_data['parameters'] is not None:
                    for param_name, param_value in product_data['parameters'].items():
                        parameter, _ = Parameter.objects.get_or_create(name=param_name)
                        ProductParameter.objects.create(
                            product_info=product_info,
                            parameter=parameter,
                            value=str(param_value)
                        )

        self.stdout.write(self.style.SUCCESS(f'Данные успешно загружены из {file_path}'))
