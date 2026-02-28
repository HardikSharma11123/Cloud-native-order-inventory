# 📦 Cloud-Native Order & Inventory Management System

A production-grade, scalable backend system for managing e-commerce orders and inventory with distributed locking to prevent race conditions.

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)
![Redis](https://img.shields.io/badge/Redis-7.0-red.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-316192.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)

## 🌟 Features

### Core Functionality
- 🔐 **JWT Authentication** with role-based access control (Customer, Admin, Warehouse Manager)
- 📦 **Product Management** - Full CRUD operations with bulk creation
- 📊 **Inventory Tracking** - Real-time stock management with reservation system
- 🛒 **Order Processing** - Complete order lifecycle from placement to delivery
- 📈 **Analytics Dashboard** - Business insights with interactive charts

### Advanced Features
- 🔒 **Redis Distributed Locking** - Prevents race conditions during concurrent order placement
- ⚡ **Asynchronous Workers** - Background task processing with Celery
- 🔄 **Real-Time Updates** - WebSocket integration for live order status
- 🎯 **Retry Logic** - Exponential backoff with jitter for transient failures
- 📋 **Inventory Reservation** - Two-phase commit pattern (reserve → confirm → release)

## 🏗️ Architecture
```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Client    │────▶│   FastAPI    │────▶│ PostgreSQL  │
│  (Browser)  │     │    Server    │     │  Database   │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ├──────────────┐
                           │              │
                    ┌──────▼─────┐  ┌────▼──────┐
                    │   Redis    │  │  Celery   │
                    │   Cache    │  │  Workers  │
                    │  & Locks   │  └───────────┘
                    └────────────┘
```

## 🚀 Tech Stack

**Backend Framework:**
- FastAPI 0.104.1
- Python 3.12

**Databases:**
- PostgreSQL 15+ (Primary database)
- Redis 7.0 (Caching & Distributed locks)

**Authentication & Security:**
- JWT tokens with passlib bcrypt
- Role-based access control (RBAC)
- Password hashing with bcrypt

**Background Processing:**
- Celery 5.3.4
- Redis as message broker

**Real-Time Communication:**
- WebSockets for live updates

**DevOps:**
- Docker & Docker Compose
- Kubernetes (production deployment)
- Alembic (database migrations)

**Frontend:**
- Vanilla JavaScript
- Chart.js for analytics
- Responsive CSS

## 📋 Prerequisites

- Python 3.12+
- PostgreSQL 15+
- Redis 7.0+
- Docker & Docker Compose (optional)

## 🔧 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/order-inventory-backend.git
cd order-inventory-backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/order_inventory
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5. Start PostgreSQL and Redis

**Using Docker:**
```bash
docker run --name postgres-order -e POSTGRES_PASSWORD=password -e POSTGRES_DB=order_inventory -p 5432:5432 -d postgres:15
docker run --name redis-order -p 6379:6379 -d redis:7
```

**Or install locally:**
- PostgreSQL: https://www.postgresql.org/download/
- Redis: https://redis.io/download/

### 6. Run Database Migrations
```bash
alembic upgrade head
```

### 7. Start the Application
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### 8. Access the Application

- **API Documentation:** http://localhost:8000/docs
- **Frontend Dashboard:** http://localhost:8000/static/index.html
- **Health Check:** http://localhost:8000/health

## 🎯 Quick Start Guide

### 1. Register Admin User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123",
    "role": "admin"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }'
```

Copy the `access_token` from the response.

### 3. Create Products (Bulk)
```bash
curl -X POST http://localhost:8000/api/v1/products/bulk \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "products": [
      {
        "name": "iPhone 15 Pro",
        "description": "Latest flagship",
        "price": 999.99,
        "category": "electronics"
      },
      {
        "name": "MacBook Pro",
        "description": "M3 chip",
        "price": 2499.99,
        "category": "electronics"
      }
    ]
  }'
```

### 4. Add Inventory
```bash
curl -X POST http://localhost:8000/api/v1/inventory/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "product_id": 1,
    "quantity": 50
  }'
```

### 5. Place an Order
```bash
curl -X POST http://localhost:8000/api/v1/orders/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "items": [
      {"product_id": 1, "quantity": 2}
    ]
  }'
```

## 📚 API Documentation

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/me` - Get current user info

### Products
- `GET /api/v1/products/` - List all products
- `GET /api/v1/products/{id}` - Get product by ID
- `GET /api/v1/products/top-selling` - Get top selling products
- `POST /api/v1/products/` - Create product (Admin)
- `POST /api/v1/products/bulk` - Bulk create products (Admin)
- `PUT /api/v1/products/{id}` - Update product (Admin)
- `DELETE /api/v1/products/{id}` - Delete product (Admin)

### Inventory
- `GET /api/v1/inventory/` - List all inventory
- `GET /api/v1/inventory/{product_id}` - Get inventory for product
- `GET /api/v1/inventory/{product_id}/available` - Get available stock
- `POST /api/v1/inventory/` - Create inventory (Admin/Warehouse)
- `PUT /api/v1/inventory/{product_id}` - Update inventory (Admin/Warehouse)

### Orders
- `POST /api/v1/orders/` - Place order
- `GET /api/v1/orders/my-orders` - Get user's orders
- `GET /api/v1/orders/{id}` - Get order details
- `GET /api/v1/orders/` - List all orders (Admin)
- `POST /api/v1/orders/{id}/confirm` - Confirm payment (Admin)
- `POST /api/v1/orders/{id}/cancel` - Cancel order
- `PUT /api/v1/orders/{id}/status` - Update order status (Admin)

### Analytics
- `GET /api/v1/analytics/dashboard-stats` - Overall statistics (Admin)
- `GET /api/v1/analytics/top-selling` - Top products by sales (Admin)
- `GET /api/v1/analytics/revenue-over-time` - Revenue trends (Admin)
- `GET /api/v1/analytics/revenue-by-product` - Revenue breakdown (Admin)

## 🔒 How Redis Locking Prevents Race Conditions

### The Problem
```
User A: Read inventory = 1
User B: Read inventory = 1  ← Both see 1 available
User A: Deduct inventory = 0
User B: Deduct inventory = -1  ← OVERSOLD!
```

### The Solution
```python
# Acquire distributed lock
with InventoryLock(product_id):
    # Only one request can execute this block at a time
    inventory = get_inventory(product_id)
    if inventory.available >= quantity:
        inventory.reserve(quantity)
        create_order()
    # Lock automatically released
```

### Implementation Details

- **SET NX** command ensures atomic lock acquisition
- **TTL (Time To Live)** prevents deadlocks if server crashes
- **Exponential backoff** with jitter prevents thundering herd
- **Retry logic** handles transient failures gracefully

## 📊 Project Structure
```
order-inventory-backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py
│   │       │   ├── products.py
│   │       │   ├── inventory.py
│   │       │   ├── orders.py
│   │       │   └── analytics.py
│   │       └── router.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── dependencies.py
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   └── init_db.py
│   ├── models/
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── inventory.py
│   │   └── order.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── inventory.py
│   │   └── order.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── product_service.py
│   │   ├── inventory_service.py
│   │   ├── order_service.py
│   │   └── analytics_service.py
│   ├── cache/
│   │   ├── redis_client.py
│   │   └── locks.py
│   └── main.py
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── app.js
│   └── index.html
├── tests/
├── alembic/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env
└── README.md
```

## 🧪 Testing

### Manual Testing via UI
1. Open http://localhost:8000/static/index.html
2. Register as admin
3. Create products and inventory
4. Switch to customer role and place orders
5. View analytics dashboard

### API Testing
Use the interactive API docs at http://localhost:8000/docs

### Load Testing (Race Condition Verification)
```bash
# Install Apache Bench
# Simulate 100 concurrent requests
ab -n 100 -c 10 -T application/json \
   -H "Authorization: Bearer TOKEN" \
   -p order.json \
   http://localhost:8000/api/v1/orders/
```

## 🐳 Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

## ☸️ Kubernetes Deployment
```bash
# Apply configurations
kubectl apply -f k8s/

# Check status
kubectl get pods
kubectl get services

# Scale deployment
kubectl scale deployment order-api --replicas=3
```

## 🎨 Frontend Features

- **Responsive Dashboard** - Works on desktop and mobile
- **Interactive Charts** - Real-time analytics visualization
- **Role-Based UI** - Different views for customers and admins
- **Shopping Cart** - Add/remove items, adjust quantities
- **Order Tracking** - Real-time order status updates
- **Product Management** - CRUD operations with inventory management

## 🔐 Security Features

- ✅ Password hashing with bcrypt
- ✅ JWT token authentication
- ✅ Role-based access control (RBAC)
- ✅ CORS protection
- ✅ SQL injection prevention (ORM)
- ✅ Input validation with Pydantic
- ✅ Secure environment variable management

## 📈 Performance Optimizations

- Connection pooling for PostgreSQL and Redis
- Database query optimization with proper indexes
- Caching frequently accessed data
- Asynchronous task processing
- Horizontal scaling capability

## 🛠️ Future Enhancements

- [ ] Implement refresh tokens for JWT
- [ ] Add email notifications with Celery
- [ ] Integrate payment gateway (Stripe/PayPal)
- [ ] Add product reviews and ratings
- [ ] Implement search with Elasticsearch
- [ ] Add monitoring with Prometheus & Grafana
- [ ] CI/CD pipeline with GitHub Actions
- [ ] API rate limiting
- [ ] WebSocket for real-time order updates

