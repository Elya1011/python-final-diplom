from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, \
    Contact, ConfirmEmailToken


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Панель управления пользователями
    """
    model = User

    fieldsets = (
        (None, {'fields': ('email', 'password', 'type')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'company', 'position')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    """
    Панель управления магазинами
    """
    model = Shop

    list_display = ['name', 'url', 'state']
    list_editable = ['url', 'state']
    list_filter = ['state']
    search_fields = ['name', 'state']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Панель управления категориями
    """
    model = Category

    list_display = ['name', 'get_shops_count']
    list_filter = ['shops']
    search_fields = ['name']
    filter_horizontal = ['shops']
    
    def get_shops_count(self, obj):
        return obj.shops.count()
    get_shops_count.short_description = 'Количество магазинов'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Панель управления продуктами
    """
    model = Product

    list_display = ['name', 'category']
    list_filter = ['category']
    search_fields = ['name', 'category__name']


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    """
    Панель управления информационным списком о продукте
    """
    model = ProductInfo

    list_display = ['product', 'shop', 'quantity', 'price', 'price_rrc']
    list_editable = ['shop', 'quantity', 'price', 'price_rrc']
    search_fields = ['product__name']
    ordering = ['product']


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    """
    Панель управления информацией о списке имен параметров
    """
    model = Parameter

    list_display = ['id', 'name']
    list_editable = ['name']
    ordering = ['id']


@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    """
    Панель управления информацией о списке параметров
    """
    model = ProductParameter

    list_display = ['product_info', 'parameter', 'value']
    list_editable = ['parameter', 'value']
    list_filter = ['parameter']
    search_fields = ['product_info__product__name']
    ordering = ['product_info']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Панель управления информацией о заказе
    """
    model = Order

    list_display = ['user', 'state', 'contact', 'dt']
    list_filter = ['state', 'dt']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Панель управления информацией о списке заказных позиций
    """
    model = OrderItem

    list_display = ['order', 'product_info', 'quantity']
    list_filter = ['order']
    search_fields = ['product_info__product__name']
    ordering = ['order']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
    Панель управления информацией о списке контактов пользователя
    """
    model = Contact

    list_display = ['user', 'city', 'phone']
    list_filter = ['city']
    ordering = ['user']


@admin.register(ConfirmEmailToken)
class ConfirmEmailTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'created_at',)
