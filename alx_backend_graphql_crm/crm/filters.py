import django_filters
from django.db import models
from .models import Customer, Product, Order


class CustomerFilter(django_filters.FilterSet):
    # Name filter - case-insensitive partial match
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    name_icontains = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    # Email filter - case-insensitive partial match
    email = django_filters.CharFilter(field_name='email', lookup_expr='icontains')
    email_icontains = django_filters.CharFilter(field_name='email', lookup_expr='icontains')

    # Created date range filters
    created_at_gte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_lte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    # Custom phone pattern filter
    phone_pattern = django_filters.CharFilter(method='filter_phone_pattern')

    def filter_phone_pattern(self, queryset, name, value):
        """Custom filter for phone number patterns (e.g., starts with +1)"""
        if value:
            return queryset.filter(phone__istartswith=value)
        return queryset

    class Meta:
        model = Customer
        fields = {
            'name': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
            'created_at': ['exact', 'gte', 'lte'],
        }


class ProductFilter(django_filters.FilterSet):
    # Name filter - case-insensitive partial match
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    name_icontains = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    # Price range filters
    price_gte = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_lte = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    # Stock range filters
    stock = django_filters.NumberFilter(field_name='stock', lookup_expr='exact')
    stock_gte = django_filters.NumberFilter(field_name='stock', lookup_expr='gte')
    stock_lte = django_filters.NumberFilter(field_name='stock', lookup_expr='lte')

    # Low stock filter (custom method)
    low_stock = django_filters.BooleanFilter(method='filter_low_stock')

    def filter_low_stock(self, queryset, name, value):
        """Filter products with low stock (less than 10)"""
        if value:
            return queryset.filter(stock__lt=10)
        return queryset

    class Meta:
        model = Product
        fields = {
            'name': ['exact', 'icontains'],
            'price': ['exact', 'gte', 'lte'],
            'stock': ['exact', 'gte', 'lte'],
        }


class OrderFilter(django_filters.FilterSet):
    # Total amount range filters
    total_amount_gte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    total_amount_lte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='lte')

    # Order date range filters
    order_date_gte = django_filters.DateTimeFilter(field_name='order_date', lookup_expr='gte')
    order_date_lte = django_filters.DateTimeFilter(field_name='order_date', lookup_expr='lte')

    # Customer name filter (related field lookup)
    customer_name = django_filters.CharFilter(
        field_name='customer__name',
        lookup_expr='icontains'
    )

    # Product name filter (related field lookup through many-to-many)
    product_name = django_filters.CharFilter(
        field_name='products__name',
        lookup_expr='icontains'
    )

    # Filter orders that include a specific product ID
    product_id = django_filters.NumberFilter(field_name='products__id')

    class Meta:
        model = Order
        fields = {
            'total_amount': ['exact', 'gte', 'lte'],
            'order_date': ['exact', 'gte', 'lte'],
            'customer__name': ['icontains'],
            'products__name': ['icontains'],
            'products__id': ['exact'],
        }