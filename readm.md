Use the superuser credentials to log in (email: admin@example.com, password: admin123)



Create the remaining role-specific dashboard templates (press_dashboard.html, delivery_dashboard.html, admin_dashboard.html)
Add more features to each dashboard based on the specific needs of each role
Implement the order management system with role-based permissions
Add more styling and polish to the UI


## How to start server

```
```bash
source venv/bin/activate
python manage.py runserver
```

---

## 👑 Admin Users

### Super Admin
📧 **Email:** `admin@irony.com`  
🔑 **Password:** `admin123`  
📱 **Phone:** +911234567890  
🔧 **Role:** ADMIN (Superuser)

### Secondary Admin
📧 **Email:** `admin2@irony.com`  
🔑 **Password:** `admin123`  
📱 **Phone:** +911234567897  
🔧 **Role:** ADMIN (Superuser)

---

## 👔 Press/Staff Users

### Press Staff 1
📧 **Email:** `press@irony.com`  
🔑 **Password:** `press123`  
📱 **Phone:** +911234567891  
👕 **Role:** PRESS

### Press Staff 2
📧 **Email:** `press2@irony.com`  
🔑 **Password:** `press123`  
📱 **Phone:** +911234567895  
👕 **Role:** PRESS

---

## 🚚 Delivery Partners

### Delivery Partner 1
📧 **Email:** `delivery@irony.com`  
🔑 **Password:** `delivery123`  
📱 **Phone:** +911234567892  
🚚 **Role:** DELIVERY

### Delivery Partner 2
📧 **Email:** `delivery2@irony.com`  
🔑 **Password:** `delivery123`  
📱 **Phone:** +911234567896  
🚚 **Role:** DELIVERY

---

## 👥 Customer Users

### Customer 1
📧 **Email:** `customer1@example.com`  
🔑 **Password:** `customer123`  
📱 **Phone:** +911234567893  
👤 **Role:** CUSTOMER

### Customer 2
📧 **Email:** `customer2@example.com`  
🔑 **Password:** `customer123`  
📱 **Phone:** +911234567894  
👤 **Role:** CUSTOMER

---

## 🛠️ How to Create These Users
Create a comprehensive order management system for a laundry service that handles order processing, tracking, and management. The system should support multiple user roles (customer, staff, admin) with appropriate permissions and workflows.

Core Features
1. User Roles & Authentication
Customers: Place, view, and track their orders
Staff: Process orders, update statuses, manage inventory
Admin: Full system access, reporting, and configuration
2. Order Processing
Order Creation
Multi-step order form with service selection
Itemized service selection (Wash & Fold, Dry Cleaning, Ironing)
Special instructions and preferences
Pickup/Delivery scheduling
Real-time price calculation
Order Status Workflow
Pending → Confirmed → In Progress → Ready for Pickup/Delivery → Completed
Cancellation and refund handling
Status update notifications
3. Service Management
Service Types
Wash & Fold
Dry Cleaning
Ironing
Special treatments (stain removal, etc.)
Pricing
Base prices per service
Additional charges (express service, special handling)
Discounts and promotions
4. Customer Interface
Dashboard
Current orders with status
Order history
Favorite services
Payment methods
Order Management
Create new orders
View order details
Track order status
Request changes/cancellations
5. Staff Interface
Order Queue
New orders
In-progress orders
Ready for pickup
Completed orders
Order Processing
Update order status
Add internal notes
Handle special requests
Manage inventory
6. Admin Features
Analytics & Reporting
Sales reports
Popular services
Customer activity
Revenue tracking
System Configuration
Service management
Pricing configuration
Staff permissions
Business hours
Technical Requirements
Backend (Django)
RESTful API endpoints
JWT Authentication
Role-based access control
Database models for orders, services, users
Background tasks for notifications
Frontend (Your choice of framework)
Responsive design
Real-time updates
Intuitive UI/UX
Form validation
Loading states and feedback
Integrations
Payment gateway
Email/SMS notifications
Calendar/scheduling
Analytics
Security
Data encryption
CSRF protection
Input validation
Rate limiting
Audit logging
User Flows
Customer Flow
Login/Register
Select services
Schedule pickup/delivery
Make payment
Track order status
Receive notifications
Provide feedback
Staff Flow
View order queue
Update order status
Handle special requests
Process payments
Generate reports
Admin Flow
View system analytics
Manage services and pricing
Handle user management
Configure system settings
Generate business reports
Success Metrics
Order processing time
Customer satisfaction
Order accuracy
System uptime
User engagement

