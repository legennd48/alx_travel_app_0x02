from django.core.management.base import BaseCommand
from listings.tasks import send_payment_confirmation_email, send_payment_failure_email
from listings.models import Payment

class Command(BaseCommand):
    help = 'Test email notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--payment-id',
            type=str,
            help='Payment ID to test email for',
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['success', 'failure'],
            default='success',
            help='Type of email to send (success or failure)',
        )

    def handle(self, *args, **options):
        payment_id = options['payment_id']
        email_type = options['type']
        
        if not payment_id:
            # Get the latest payment for testing
            try:
                payment = Payment.objects.latest('payment_id')
                payment_id = str(payment.payment_id)
                self.stdout.write(f"Using latest payment: {payment_id}")
            except Payment.DoesNotExist:
                self.stdout.write(self.style.ERROR('No payments found. Create a payment first.'))
                return
        
        self.stdout.write(f"Sending {email_type} email for payment: {payment_id}")
        
        if email_type == 'success':
            result = send_payment_confirmation_email.delay(payment_id)
        else:
            result = send_payment_failure_email.delay(payment_id)
        
        self.stdout.write(
            self.style.SUCCESS(f'Email task queued successfully. Task ID: {result.id}')
        )
