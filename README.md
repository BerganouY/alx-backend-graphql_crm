# ALX Backend GraphQL CRM

A comprehensive Customer Relationship Management (CRM) system built with Django and GraphQL. This project demonstrates advanced GraphQL concepts including mutations, filtering, and complex data relationships.

## 🚀 Features

- **GraphQL API** with mutations and queries
- **Customer Management** with validation and bulk operations
- **Product Catalog** with inventory tracking
- **Order Processing** with automatic total calculations
- **Advanced Filtering** with multiple criteria
- **Data Relationships** between customers, products, and orders
- **Error Handling** with user-friendly messages
- **Admin Interface** for easy data management
- **Database Seeding** for testing and development

## 📋 Table of Contents

- [Installation](#installation)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Usage](#usage)
- [GraphQL Schema](#graphql-schema)
- [API Examples](#api-examples)
- [Testing](#testing)
- [Contributing](#contributing)

## 🛠 Installation

### Prerequisites

- Python 3.8+
- Django 4.2+
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/alx-backend-graphql_crm.git
   cd alx-backend-graphql_crm
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Seed the database (optional)**
   ```bash
   python manage.py seed_db --clear
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - GraphQL Playground: http://localhost:8000/graphql/
   - Django Admin: http://localhost:8000/admin/

## 📁 Project Structure

```
alx-backend-graphql_crm/
├── alx_backend_graphql_crm/
│   ├── __init__.py
│   ├── settings.py          # Django settings with GraphQL config
│   ├── urls.py             # URL routing including GraphQL endpoint
│   ├── wsgi.py
│   └── schema.py           # Main GraphQL schema
├── crm/
│   ├── __init__.py
│   ├── admin.py            # Django admin configuration
│   ├── apps.py
│   ├── models.py           # Data models (Customer, Product, Order)
│   ├── schema.py           # GraphQL queries and mutations
│   ├── filters.py          # Django-filter configurations
│   ├── migrations/         # Database migrations
│   ├── management/
│   │   └── commands/
│   │       └── seed_db.py  # Database seeding command
│   ├── tests.py
│   └── views.py
├── manage.py
├── seed_db.py              # Standalone seeding script
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## ⚙️ Configuration

### Django Settings

Key configurations in `settings.py`:

```python
INSTALLED_APPS = [
    # ... Django apps
    'graphene_django',
    'django_filters',
    'crm',
]

GRAPHENE = {
    'SCHEMA': 'alx_backend_graphql_crm.schema.schema'
}
```

### Database Models

The application includes three main models:

- **Customer**: Stores customer information with email validation
- **Product**: Manages product catalog with price and inventory
- **Order**: Handles order processing with many-to-many product relationships

## 🎯 Usage

### GraphQL Endpoint

Access the GraphQL playground at: `http://localhost:8000/graphql/`

### Basic Query

```graphql
{
  hello
}
```

### Database Operations

```bash
# Seed database with sample data
python manage.py seed_db

# Clear and reseed database
python manage.py seed_db --clear

# Access Django shell
python manage.py shell
```

## 📊 GraphQL Schema

### Types

- **CustomerType**: Customer information and relationships
- **ProductType**: Product details with pricing and inventory
- **OrderType**: Order details with customer and product associations

### Queries

- `hello`: Simple greeting query
- `allCustomers`: Filtered customer list with pagination
- `allProducts`: Filtered product list with pagination  
- `allOrders`: Filtered order list with pagination
- `customer(id)`: Single customer by ID
- `product(id)`: Single product by ID
- `order(id)`: Single order by ID

### Mutations

- `createCustomer`: Create a new customer with validation
- `bulkCreateCustomers`: Create multiple customers with partial success handling
- `createProduct`: Create a new product with business logic validation
- `createOrder`: Create an order with automatic total calculation

## 🔍 API Examples

### Customer Operations

#### Create a Customer
```graphql
mutation {
  createCustomer(input: {
    name: "John Doe"
    email: "john.doe@example.com"
    phone: "+1234567890"
  }) {
    customer {
      id
      name
      email
      phone
      createdAt
    }
    message
    success
    errors
  }
}
```

#### Bulk Create Customers
```graphql
mutation {
  bulkCreateCustomers(input: [
    {name: "Alice Johnson", email: "alice@example.com", phone: "+1111111111"},
    {name: "Bob Smith", email: "bob@example.com", phone: "222-333-4444"}
  ]) {
    customers {
      id
      name
      email
    }
    errors
    successCount
    errorCount
  }
}
```

#### Query Customers with Filters
```graphql
{
  allCustomers(filter: {
    nameIcontains: "John"
    createdAtGte: "2024-01-01"
    phonePattern: "+1"
  }) {
    edges {
      node {
        id
        name
        email
        phone
        createdAt
      }
    }
  }
}
```

### Product Operations

#### Create a Product
```graphql
mutation {
  createProduct(input: {
    name: "Gaming Laptop"
    price: 1299.99
    stock: 25
  }) {
    product {
      id
      name
      price
      stock
      createdAt
    }
    success
    errors
  }
}
```

#### Query Products with Filters
```graphql
{
  allProducts(filter: {
    priceGte: 100
    priceLte: 2000
    stockGte: 10
    lowStock: false
  }) {
    edges {
      node {
        id
        name
        price
        stock
      }
    }
  }
}
```

### Order Operations

#### Create an Order
```graphql
mutation {
  createOrder(input: {
    customerId: "1"
    productIds: ["1", "2", "3"]
  }) {
    order {
      id
      customer {
        name
        email
      }
      products {
        name
        price
      }
      totalAmount
      orderDate
    }
    success
    errors
  }
}
```

#### Query Orders with Filters
```graphql
{
  allOrders(filter: {
    totalAmountGte: 500
    orderDateGte: "2024-01-01"
    customerName: "John"
    productName: "Laptop"
  }) {
    edges {
      node {
        id
        customer {
          name
        }
        products {
          name
          price
        }
        totalAmount
        orderDate
      }
    }
  }
}
```

## 🔧 Advanced Filtering

The system supports comprehensive filtering options:

### Customer Filters
- `name` / `nameIcontains`: Filter by customer name
- `email` / `emailIcontains`: Filter by email address
- `createdAtGte` / `createdAtLte`: Filter by creation date range
- `phonePattern`: Filter by phone number pattern

### Product Filters
- `name` / `nameIcontains`: Filter by product name
- `priceGte` / `priceLte`: Filter by price range
- `stockGte` / `stockLte`: Filter by stock quantity
- `lowStock`: Filter products with stock < 10

### Order Filters
- `totalAmountGte` / `totalAmountLte`: Filter by order total
- `orderDateGte` / `orderDateLte`: Filter by order date range
- `customerName`: Filter by customer name
- `productName`: Filter by product name
- `productId`: Filter orders containing specific product

## 🧪 Testing

### Manual Testing

Use the GraphiQL interface at `http://localhost:8000/graphql/` to test all queries and mutations.

### Sample Test Cases

1. **Customer Creation**
   - Valid customer data
   - Duplicate email validation
   - Invalid phone format handling

2. **Bulk Operations**
   - Partial success scenarios
   - Error handling for invalid data

3. **Product Management**
   - Price validation (positive values)
   - Stock validation (non-negative)

4. **Order Processing**
   - Customer existence validation
   - Product existence validation
   - Automatic total calculation

### Database Validation

```bash
# Check data integrity
python manage.py shell

# In the shell:
from crm.models import Customer, Product, Order
print(f"Customers: {Customer.objects.count()}")
print(f"Products: {Product.objects.count()}")
print(f"Orders: {Order.objects.count()}")
```

## 🐛 Troubleshooting

### Common Issues

1. **GraphQL Schema Error**
   ```bash
   # Ensure proper imports in schema.py
   python manage.py shell -c "import alx_backend_graphql_crm.schema"
   ```

2. **Migration Issues**
   ```bash
   # Reset migrations if needed
   python manage.py migrate --run-syncdb
   ```

3. **Seeding Problems**
   ```bash
   # Clear database and reseed
   python manage.py seed_db --clear
   ```

### Performance Considerations

- Use `select_related()` and `prefetch_related()` for complex queries
- Implement pagination for large datasets
- Consider database indexing for frequently filtered fields

## 📚 Dependencies

- **Django**: Web framework
- **graphene-django**: GraphQL integration
- **django-filter**: Advanced filtering capabilities

See `requirements.txt` for exact versions.

**Happy coding! 🚀**