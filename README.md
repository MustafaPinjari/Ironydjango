# Ironyy - Premium Laundry Service

A comprehensive Django-based laundry service management system with REST API capabilities and modern frontend.

## 🚀 Features

- **User Authentication** - Secure registration, login, and password management
- **Order Management** - Track and manage laundry orders
- **Service Customization** - Multiple service types and variants
- **Admin Dashboard** - Full-featured admin interface
- **REST API** - For mobile app integration
- **Responsive Design** - Works on all devices

## 🛠️ Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)
- Git
- Virtual environment (recommended)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ironyy.git
cd ironyy
```

### 2. Set Up Virtual Environment

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the project root:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://username:password@localhost/ironyy
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend  # For development
DEFAULT_FROM_EMAIL=admin@ironyy.com
```

### 5. Database Setup

1. Create a PostgreSQL database:
   ```sql
   CREATE DATABASE ironyy;
   CREATE USER ironyyuser WITH PASSWORD 'yourpassword';
   GRANT ALL PRIVILEGES ON DATABASE ironyy TO ironyyuser;
   ```

2. Run migrations:
   ```bash
   python manage.py migrate
   ```

### 6. Create Superuser

```bash
python manage.py createsuperuser
# Follow prompts to create admin account
```

### 7. Populate Initial Data

To seed the database with default services, variants, and test data:

```bash
python manage.py loaddata initial_data.json
```

### 8. Run Development Server

```bash
python manage.py runserver
```

Access the application at `http://127.0.0.1:8000/`
Admin interface: `http://127.0.0.1:8000/admin/`

## 🔧 Default Credentials

- **Admin Panel**: `http://127.0.0.1:8000/admin/`
  - Username: admin@ironyy.com
  - Password: admin123

- **Test User**:
  - Email: user@example.com
  - Password: testpass123

## 📦 Data Population

### Default Services and Variants

The system comes with pre-defined services and variants. These can be managed through the admin panel:

1. **Services**:
   - Wash & Fold
   - Dry Cleaning
   - Ironing
   - Premium Laundry

2. **Variants**:
   - Regular (24h)
   - Express (12h)
   - Same Day (6h)

To add or modify services/variants:
1. Log in to the admin panel
2. Navigate to "Services" or "Variants" section
3. Add/Edit/Delete as needed

### Sample Data

To populate the database with sample orders and test data:

```bash
python manage.py loaddata sample_data.json
```

## 🔄 Database Migrations

When making changes to models:

```bash
# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

## 🛠️ Development

### Running Tests

```bash
python manage.py test
```

### Linting

```bash
flake8 .
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DEBUG | Enable debug mode | False |
| SECRET_KEY | Django secret key | - |
| DATABASE_URL | Database connection URL | - |
| EMAIL_BACKEND | Email backend | console |
| ALLOWED_HOSTS | Allowed hostnames | ['*'] |

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support, please open an issue in the GitHub repository.
```
ironyy/
├── accounts/               # User authentication and profiles
├── api/                    # REST API endpoints
├── core/                   # Core functionality and settings
├── dashboard/              # User dashboard views
├── ironyy/                 # Main app configuration
├── orders/                 # Order management
├── static/                 # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
├── templates/              # HTML templates
│   ├── base/
│   └── ironyy/
├── .env                    # Environment variables
├── .gitignore
├── manage.py
├── package.json
├── README.md
└── requirements.txt
```

## Development

### Running Tests

```bash
python manage.py test
```

### Code Style

This project uses:
- Flake8 for Python code style checking
- Prettier for HTML/CSS/JS formatting

### Git Workflow

1. Create a new branch for your feature: `git checkout -b feature/your-feature-name`
2. Make your changes and commit them
3. Push to the branch: `git push origin feature/your-feature-name`
4. Create a pull request

## Deployment

### Production Settings

For production, ensure you:
1. Set `DEBUG=False` in your environment variables
2. Configure a production database
3. Set up a proper web server (Nginx/Apache with Gunicorn/uWSGI)
4. Configure HTTPS with Let's Encrypt

### Docker (Optional)

```bash
# Build the Docker image
docker-compose build

# Run the application
docker-compose up -d
```

## Troubleshooting

- **Database connection issues**: Verify your database credentials in the `.env` file
- **Static files not loading**: Run `python manage.py collectstatic`
- **Missing dependencies**: Ensure all packages in `requirements.txt` are installed

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🏗️ System Architecture Q&A

### 1. What is the overall architecture of the application?
The application follows a **3-tier architecture**:
- **Presentation Layer**: Django templates with responsive frontend (HTML, CSS, JavaScript)
- **Application Layer**: Django framework handling business logic and API endpoints
- **Data Layer**: PostgreSQL database with Django ORM for data persistence

### 2. How is the database structured?
- **Relational Database**: PostgreSQL for data integrity and complex queries
- **Key Models**:
  - `User`: Authentication and user profiles
  - `Order`: Laundry service requests
  - `Service`: Different types of laundry services
  - `Variant`: Service options and customizations
  - `Payment`: Transaction records

### 3. How does authentication and authorization work?
- **Authentication**: Custom user model with email-based authentication
- **Authorization**: Role-based access control (RBAC) with groups and permissions
- **Security**: Argon2 password hashing, CSRF protection, and secure session management

### 4. What are the key API endpoints?
- `/api/auth/`: Authentication endpoints (login, register, token refresh)
- `/api/orders/`: Order management
- `/api/services/`: Service catalog
- `/api/users/`: User profile management

### 5. How is the frontend structured?
- **Templates**: Django template language with template inheritance
- **Static Files**: Organized by type (CSS, JS, images)
- **Responsive Design**: Mobile-first approach using modern CSS (Flexbox/Grid)

### 6. What are the deployment considerations?
- **Web Server**: Nginx as reverse proxy
- **Application Server**: Gunicorn for WSGI
- **Database**: PostgreSQL with regular backups
- **Caching**: Redis for session management and caching
- **Media Storage**: AWS S3 or similar for static and media files

### 7. How does the system handle scalability?
- **Horizontal Scaling**: Stateless architecture allows multiple app servers
- **Database**: Read replicas for read-heavy operations
- **Caching**: Redis for frequently accessed data
- **Background Tasks**: Celery for asynchronous processing

### 8. What are the security measures in place?
- **Data Protection**: Encryption at rest and in transit (HTTPS)
- **Authentication**: Secure password hashing with Argon2
- **Input Validation**: Form and model validation
- **Security Headers**: CSP, XSS protection, HSTS
- **Rate Limiting**: Protection against brute force attacks

### 9. How is the application monitored?
- **Error Tracking**: Sentry for error monitoring
- **Logging**: Structured logging with rotation
- **Performance**: New Relic or similar APM tool
- **Uptime**: Health check endpoints and monitoring

### 10. What are the potential points of failure and their mitigation?
- **Database**: Replication and regular backups
- **Third-party Services**: Circuit breakers and fallback mechanisms
- **High Traffic**: Auto-scaling and CDN for static assets
- **Data Loss**: Regular backups and point-in-time recovery
