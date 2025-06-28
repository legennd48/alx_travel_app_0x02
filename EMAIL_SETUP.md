# Email Notifications Setup

## Overview
This implementation uses Celery with Redis as a message broker to send asynchronous email notifications for payment confirmations and failures.

## Components

### 1. Celery Configuration
- **File**: `alx_travel_app/celery.py`
- **Purpose**: Configure Celery app with Django integration

### 2. Email Tasks
- **File**: `listings/tasks.py`
- **Tasks**:
  - `send_payment_confirmation_email(payment_id)` - Sends success email
  - `send_payment_failure_email(payment_id)` - Sends failure email

### 3. Integration Points
- **PaymentCallbackView**: Sends emails based on Chapa verification
- **PaymentSuccessView**: Sends confirmation email on success
- **PaymentFailureView**: Sends failure email on failed payments

## Setup Instructions

### 1. Install Redis
```bash
# Ubuntu/Debian
sudo apt install redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### 2. Start Celery Worker
```bash
# In project directory
cd /home/legennd/Software_repos/alx_travel_app_0x02/alx_travel_app
./start_celery.sh
```

### 3. Test Email Functionality
```bash
# Test with latest payment
python manage.py test_email --type=success

# Test with specific payment ID
python manage.py test_email --payment-id=PAYMENT_UUID --type=failure
```

## Email Configuration

### Development (Console Backend)
- Emails are printed to console
- No SMTP configuration needed

### Production (SMTP Backend)
Update settings.py:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
```

Add to .env:
```
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Monitoring
- Check Celery worker logs for task execution
- Monitor Redis for queued tasks
- Email logs appear in Django console (development) or mail server logs (production)

## Testing Payment Flow

1. Create a booking
2. Initiate payment via API
3. Complete payment on Chapa
4. Check email output in console or email client
5. Verify payment status in database
