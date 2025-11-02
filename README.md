# Ironyy - Premium Laundry Service

A modern web application for managing laundry services with an intuitive user interface and robust backend functionality.

## Features

- User authentication and authorization
- Order management system
- Service scheduling and tracking
- Responsive design for all devices
- Secure payment integration
- Admin dashboard

## Prerequisites

Before you begin, ensure you have the following installed on your Windows system:

- Python 3.8 or higher
- pip (Python package manager)
- Git
- PostgreSQL (or your preferred database)
- Node.js and npm (for frontend assets)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ironyy.git
cd ironyy
```

### 2. Create and Activate Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows Command Prompt:
venv\Scripts\activate
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root with the following variables:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://username:password@localhost/ironyy
EMAIL_HOST=your-email-host
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
```

### 5. Set Up Database

1. Install PostgreSQL if you haven't already
2. Create a new database named `ironyy`
3. Run migrations:

```bash
python manage.py migrate
```

### 6. Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

### 7. Install Frontend Dependencies

```bash
# Navigate to the project root if not already there
cd /path/to/ironyy

# Install Node.js dependencies
npm install

# Build static files
npm run build

# Or for development with hot-reload
npm run dev
```

### 8. Collect Static Files

```bash
python manage.py collectstatic
```

### 9. Run the Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser to see the application.

## Project Structure

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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For any questions or feedback, please contact us at support@ironyy.com
