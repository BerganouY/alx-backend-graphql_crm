import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.core.exceptions import ValidationError
from django.db import transaction
from decimal import Decimal
from datetime import datetime
import re

from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter


# GraphQL Object Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"
        filter_fields = {
            'name': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
            'created_at': ['exact', 'gte', 'lte'],
        }
        interfaces = (graphene.relay.Node,)


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"
        filter_fields = {
            'name': ['exact', 'icontains'],
            'price': ['exact', 'gte', 'lte'],
            'stock': ['exact', 'gte', 'lte'],
        }
        interfaces = (graphene.relay.Node,)


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"
        filter_fields = {
            'total_amount': ['exact', 'gte', 'lte'],
            'order_date': ['exact', 'gte', 'lte'],
        }
        interfaces = (graphene.relay.Node,)


# Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int(required=False, default_value=0)


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime(required=False)


# Validation helpers
def validate_email_unique(email, exclude_id=None):
    """Validate that email is unique"""
    query = Customer.objects.filter(email=email)
    if exclude_id:
        query = query.exclude(id=exclude_id)
    if query.exists():
        raise ValidationError("Email already exists")


def validate_phone_format(phone):
    """Validate phone number format"""
    if phone:
        pattern = r'^\+?1?\d{9,15}$|^\d{3}-\d{3}-\d{4}$'
        if not re.match(pattern, phone):
            raise ValidationError("Invalid phone number format")


# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, input):
        errors = []

        try:
            # Validate email uniqueness
            validate_email_unique(input.email)

            # Validate phone format
            if input.phone:
                validate_phone_format(input.phone)

            # Create customer
            customer = Customer.objects.create(
                name=input.name,
                email=input.email,
                phone=input.phone if input.phone else None
            )

            return CreateCustomer(
                customer=customer,
                message="Customer created successfully!",
                success=True,
                errors=[]
            )

        except ValidationError as e:
            errors.extend(e.messages if hasattr(e, 'messages') else [str(e)])
        except Exception as e:
            errors.append(str(e))

        return CreateCustomer(
            customer=None,
            message="Failed to create customer",
            success=False,
            errors=errors
        )


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)
    success_count = graphene.Int()
    error_count = graphene.Int()

    @staticmethod
    def mutate(root, info, input):
        created_customers = []
        errors = []

        with transaction.atomic():
            for i, customer_data in enumerate(input):
                try:
                    # Validate email uniqueness
                    validate_email_unique(customer_data.email)

                    # Validate phone format
                    if customer_data.phone:
                        validate_phone_format(customer_data.phone)

                    # Create customer
                    customer = Customer.objects.create(
                        name=customer_data.name,
                        email=customer_data.email,
                        phone=customer_data.phone if customer_data.phone else None
                    )
                    created_customers.append(customer)

                except ValidationError as e:
                    error_msg = f"Customer {i + 1} ({customer_data.email}): {e.messages[0] if hasattr(e, 'messages') else str(e)}"
                    errors.append(error_msg)
                except Exception as e:
                    error_msg = f"Customer {i + 1} ({customer_data.email}): {str(e)}"
                    errors.append(error_msg)

        return BulkCreateCustomers(
            customers=created_customers,
            errors=errors,
            success_count=len(created_customers),
            error_count=len(errors)
        )


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    message = graphene.String()
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, input):
        errors = []

        try:
            # Validate price is positive
            if input.price <= 0:
                raise ValidationError("Price must be positive")

            # Validate stock is non-negative
            if input.stock < 0:
                raise ValidationError("Stock cannot be negative")

            # Create product
            product = Product.objects.create(
                name=input.name,
                price=input.price,
                stock=input.stock
            )

            return CreateProduct(
                product=product,
                message="Product created successfully!",
                success=True,
                errors=[]
            )

        except ValidationError as e:
            errors.extend(e.messages if hasattr(e, 'messages') else [str(e)])
        except Exception as e:
            errors.append(str(e))

        return CreateProduct(
            product=None,
            message="Failed to create product",
            success=False,
            errors=errors
        )


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)
    message = graphene.String()
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, input):
        errors = []

        try:
            # Validate customer exists
            try:
                customer = Customer.objects.get(id=input.customer_id)
            except Customer.DoesNotExist:
                raise ValidationError("Customer not found")

            # Validate at least one product is provided
            if not input.product_ids:
                raise ValidationError("At least one product must be selected")

            # Validate all products exist
            products = Product.objects.filter(id__in=input.product_ids)
            if products.count() != len(input.product_ids):
                raise ValidationError("One or more products not found")

            # Create order
            with transaction.atomic():
                order = Order.objects.create(
                    customer=customer,
                    order_date=input.order_date if input.order_date else datetime.now()
                )

                # Add products and calculate total
                order.products.set(products)
                total_amount = sum(product.price for product in products)
                order.total_amount = total_amount
                order.save()

            return CreateOrder(
                order=order,
                message="Order created successfully!",
                success=True,
                errors=[]
            )

        except ValidationError as e:
            errors.extend(e.messages if hasattr(e, 'messages') else [str(e)])
        except Exception as e:
            errors.append(str(e))

        return CreateOrder(
            order=None,
            message="Failed to create order",
            success=False,
            errors=errors
        )


# Query Class
class Query(graphene.ObjectType):
    hello = graphene.String()

    # Basic queries
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)

    # Single object queries
    customer = graphene.Field(CustomerType, id=graphene.ID())
    product = graphene.Field(ProductType, id=graphene.ID())
    order = graphene.Field(OrderType, id=graphene.ID())

    def resolve_hello(self, info):
        return "Hello, GraphQL!"

    def resolve_customer(self, info, id):
        try:
            return Customer.objects.get(id=id)
        except Customer.DoesNotExist:
            return None

    def resolve_product(self, info, id):
        try:
            return Product.objects.get(id=id)
        except Product.DoesNotExist:
            return None

    def resolve_order(self, info, id):
        try:
            return Order.objects.get(id=id)
        except Order.DoesNotExist:
            return None


# Mutation Class
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()