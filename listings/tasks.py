from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Payment
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_payment_confirmation_email(payment_id):
    """
    Send confirmation email after successful payment
    """
    try:
        payment = Payment.objects.get(payment_id=payment_id)
        booking = payment.booking
        
        subject = f'Payment Confirmation - Booking {booking.booking_id}'
        message = f'''
Dear {booking.user},

Your payment has been successfully processed!

Booking Details:
- Booking ID: {booking.booking_id}
- Listing: {booking.listing.title}
- Amount Paid: ETB {payment.amount}
- Transaction ID: {payment.transaction_id}
- Check-in: {booking.start_date}
- Check-out: {booking.end_date}
- Payment Status: {payment.payment_status}

Thank you for choosing ALX Travel App for your booking!

Best regards,
ALX Travel Team
        '''
        
        # For development, we'll use a default email
        # In production, you'd get this from booking.user.email
        recipient_email = 'legennd48@gmail.com'  # Replace with actual user email when available
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
        )
        
        logger.info(f"Payment confirmation email sent successfully for payment {payment_id}")
        return f"Email sent successfully for payment {payment_id}"
        
    except Payment.DoesNotExist:
        logger.error(f"Payment {payment_id} not found")
        return f"Payment {payment_id} not found"
    except Exception as e:
        logger.error(f"Error sending email for payment {payment_id}: {str(e)}")
        return f"Error sending email: {str(e)}"

@shared_task
def send_payment_failure_email(payment_id):
    """
    Send notification email when payment fails
    """
    try:
        payment = Payment.objects.get(payment_id=payment_id)
        booking = payment.booking
        
        subject = f'Payment Failed - Booking {booking.booking_id}'
        message = f'''
Dear {booking.user},

We're sorry to inform you that your payment could not be processed.

Booking Details:
- Booking ID: {booking.booking_id}
- Listing: {booking.listing.title}
- Amount: ETB {payment.amount}
- Transaction ID: {payment.transaction_id}
- Payment Status: {payment.payment_status}

Please try again or contact our support team if you need assistance.

Best regards,
ALX Travel Team
        '''
        
        recipient_email = 'legennd48@gmail.com'  # Replace with actual user email when available
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
        )
        
        logger.info(f"Payment failure email sent successfully for payment {payment_id}")
        return f"Failure email sent successfully for payment {payment_id}"
        
    except Payment.DoesNotExist:
        logger.error(f"Payment {payment_id} not found")
        return f"Payment {payment_id} not found"
    except Exception as e:
        logger.error(f"Error sending failure email for payment {payment_id}: {str(e)}")
        return f"Error sending failure email: {str(e)}"
