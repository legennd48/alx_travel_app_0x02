from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer, PaymentSerializer
from .tasks import send_payment_confirmation_email, send_payment_failure_email
import requests
import json
import uuid

# Create your views here.

class ListingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows listings to be viewed or edited.
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

class BookingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows bookings to be viewed or edited.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows payments to be viewed or edited.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def create(self, request, *args, **kwargs):
        """
        Override create method to return Chapa payment link in response
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create the payment record
        payment = serializer.save()
        
        # After creating the payment record, initiate payment with Chapa
        try:
            chapa_response, tx_ref = self.initiate_chapa_payment(payment)
            if chapa_response.get('status') == 'success':
                # Update payment with transaction details using our generated tx_ref
                payment.transaction_id = tx_ref
                payment.save()
                
                # Return payment data along with Chapa checkout URL
                payment_data = serializer.data
                payment_data.update({
                    'chapa_status': 'success',
                    'checkout_url': chapa_response['data']['checkout_url'],
                    'tx_ref': tx_ref,
                    'message': 'Payment initiated successfully. Please complete payment using the checkout URL.'
                })
                
                headers = self.get_success_headers(serializer.data)
                return Response(payment_data, status=status.HTTP_201_CREATED, headers=headers)
            else:
                # Chapa initiation failed
                payment.payment_status = 'failed'
                payment.save()
                
                payment_data = serializer.data
                payment_data.update({
                    'chapa_status': 'failed',
                    'error': 'Failed to initiate payment with Chapa',
                    'details': chapa_response
                })
                
                headers = self.get_success_headers(serializer.data)
                return Response(payment_data, status=status.HTTP_201_CREATED, headers=headers)
                
        except Exception as e:
            # Log error and keep payment in pending status
            print(f"Error initiating Chapa payment: {str(e)}")
            
            payment_data = serializer.data
            payment_data.update({
                'chapa_status': 'error',
                'error': f'Error initiating Chapa payment: {str(e)}'
            })
            
            headers = self.get_success_headers(serializer.data)
            return Response(payment_data, status=status.HTTP_201_CREATED, headers=headers)

    def initiate_chapa_payment(self, payment):
        """
        Make POST request to Chapa API to initiate payment
        Returns: (chapa_response, tx_ref)
        """
        # Chapa API endpoint
        url = f"{settings.CHAPA_API_URL}/initialize"

        # Generate unique transaction reference
        tx_ref = f"booking-{payment.booking.booking_id}-{uuid.uuid4().hex[:8]}"
        
        # Prepare payload for Chapa API
        payload = {
            "amount": str(payment.amount),
            "currency": "ETB",
            "email": "legennd48@gmail.com",  # Since user is CharField, add email domain
            "first_name": payment.booking.user.split()[0] if ' ' in payment.booking.user else payment.booking.user,
            "last_name": payment.booking.user.split()[-1] if ' ' in payment.booking.user else "Guest",
            "phone_number": "0900123456",  # Since user is CharField, use default phone
            "tx_ref": tx_ref,
            "callback_url": settings.CALLBACK_URL,
            "return_url": settings.PAYMENT_SUCCESS_URL,
            "customization": {
                "title": "Booking Payment",
                "description": f"Booking from {payment.booking.start_date} to {payment.booking.end_date}"
            }
        }
        
        # Set headers with authorization
        headers = {
            'Authorization': f'Bearer {settings.CHAPA_SECRET_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Make POST request to Chapa API
        response = requests.post(url, json=payload, headers=headers)
        
        # Return both the response data and the tx_ref we generated
        return response.json(), tx_ref

    @action(detail=True, methods=['post'])
    def verify_payment(self, request, pk=None):
        """
        Custom action to verify payment status with Chapa
        """
        try:
            payment = self.get_object()
            
            if not payment.transaction_id:
                return Response(
                    {"error": "No transaction ID found for this payment"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verify payment with Chapa
            verification_response = self.verify_chapa_payment(payment.transaction_id)
            
            if verification_response.get('status') == 'success':
                payment_data = verification_response['data']
                
                # Update payment status based on Chapa response
                if payment_data['status'] == 'success':
                    payment.payment_status = 'completed'
                elif payment_data['status'] == 'failed':
                    payment.payment_status = 'failed'
                
                payment.save()
                
                return Response({
                    "message": "Payment verification successful",
                    "payment_status": payment.payment_status,
                    "chapa_status": payment_data['status']
                })
            else:
                return Response(
                    {"error": "Failed to verify payment with Chapa"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {"error": f"Error verifying payment: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def verify_chapa_payment(self, tx_ref):
        """
        Make GET request to Chapa API to verify payment status
        """
        url = f"https://api.chapa.co/v1/transaction/verify/{tx_ref}"
        
        headers = {
            'Authorization': f'Bearer {settings.CHAPA_SECRET_KEY}',
        }
        
        response = requests.get(url, headers=headers)
        return response.json()

    @action(detail=False, methods=['post'])
    def initiate_payment(self, request):
        """
        Custom action to initiate payment for a booking
        """
        try:
            booking_id = request.data.get('booking_id')
            amount = request.data.get('amount')
            
            if not booking_id or not amount:
                return Response(
                    {"error": "booking_id and amount are required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get the booking
            try:
                booking = Booking.objects.get(booking_id=booking_id)
            except Booking.DoesNotExist:
                return Response(
                    {"error": "Booking not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Create payment record
            payment = Payment.objects.create(
                booking=booking,
                amount=amount,
                payment_status='pending'
            )
            
            # Initiate payment with Chapa
            chapa_response, tx_ref = self.initiate_chapa_payment(payment)
            
            if chapa_response.get('status') == 'success':
                # Update payment with transaction ID using our generated tx_ref
                payment.transaction_id = tx_ref
                payment.save()
                
                return Response({
                    "message": "Payment initiated successfully",
                    "payment_id": payment.payment_id,
                    "checkout_url": chapa_response['data']['checkout_url'],
                    "tx_ref": tx_ref
                })
            else:
                payment.payment_status = 'failed'
                payment.save()
                
                return Response(
                    {"error": "Failed to initiate payment with Chapa", "details": chapa_response}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {"error": f"Error initiating payment: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Payment Success and Callback Views
class PaymentSuccessView(View):
    """
    View to handle successful payment returns from Chapa
    """
    def get(self, request):
        """
        Handle GET request when user is redirected back after successful payment
        """
        # Get transaction reference from URL parameters
        tx_ref = request.GET.get('tx_ref')
        status_param = request.GET.get('status')
        
        context = {
            'tx_ref': tx_ref,
            'status': status_param,
            'success': status_param == 'success'
        }
        
        if tx_ref and status_param == 'success':
            try:
                # Find the payment record by transaction ID
                payment = Payment.objects.get(transaction_id=tx_ref)
                
                # Update payment status if not already completed
                if payment.payment_status != 'completed':
                    payment.payment_status = 'completed'
                    payment.save()
                    
                    # Send confirmation email using Celery
                    send_payment_confirmation_email.delay(str(payment.payment_id))
                
                context.update({
                    'payment': payment,
                    'booking': payment.booking,
                    'listing': payment.booking.listing,
                    'amount': payment.amount
                })
                
            except Payment.DoesNotExist:
                context['error'] = 'Payment record not found'
        
        return render(request, 'payments/success.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class PaymentCallbackView(View):
    """
    View to handle payment verification callbacks from Chapa
    """
    def post(self, request):
        """
        Handle POST callback from Chapa after payment completion
        """
        try:
            # Parse JSON data from Chapa
            data = json.loads(request.body)
            
            tx_ref = data.get('tx_ref')
            status_param = data.get('status')
            
            if not tx_ref:
                return JsonResponse({'error': 'Transaction reference not provided'}, status=400)
            
            # Find the payment record
            try:
                payment = Payment.objects.get(transaction_id=tx_ref)
            except Payment.DoesNotExist:
                return JsonResponse({'error': 'Payment record not found'}, status=404)
            
            # Verify payment with Chapa API to ensure callback is legitimate
            verification_response = self.verify_with_chapa(tx_ref)
            
            if verification_response.get('status') == 'success':
                payment_data = verification_response['data']
                
                # Update payment status based on Chapa verification
                if payment_data['status'] == 'success':
                    payment.payment_status = 'completed'
                    payment.save()
                    
                    # Send confirmation email using Celery
                    send_payment_confirmation_email.delay(str(payment.payment_id))
                    
                elif payment_data['status'] == 'failed':
                    payment.payment_status = 'failed'
                    payment.save()
                    
                    # Send failure email using Celery
                    send_payment_failure_email.delay(str(payment.payment_id))
                    
                else:
                    payment.payment_status = 'pending'
                    payment.save()
                
                return JsonResponse({
                    'message': 'Payment status updated successfully',
                    'status': payment.payment_status
                })
            else:
                return JsonResponse({'error': 'Failed to verify payment with Chapa'}, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Error processing callback: {str(e)}'}, status=500)
    
    def verify_with_chapa(self, tx_ref):
        """
        Verify payment status with Chapa API
        """
        url = f"https://api.chapa.co/v1/transaction/verify/{tx_ref}"
        
        headers = {
            'Authorization': f'Bearer {settings.CHAPA_SECRET_KEY}',
        }
        
        response = requests.get(url, headers=headers)
        return response.json()


class PaymentFailureView(View):
    """
    View to handle failed payment returns from Chapa
    """
    def get(self, request):
        """
        Handle GET request when user is redirected back after failed payment
        """
        tx_ref = request.GET.get('tx_ref')
        status_param = request.GET.get('status')
        
        context = {
            'tx_ref': tx_ref,
            'status': status_param,
            'failed': True
        }
        
        if tx_ref:
            try:
                # Find the payment record by transaction ID
                payment = Payment.objects.get(transaction_id=tx_ref)
                
                # Update payment status to failed
                if payment.payment_status != 'failed':
                    payment.payment_status = 'failed'
                    payment.save()
                    
                    # Send failure email using Celery
                    send_payment_failure_email.delay(str(payment.payment_id))
                
                context.update({
                    'payment': payment,
                    'booking': payment.booking,
                    'listing': payment.booking.listing,
                    'amount': payment.amount
                })
                
            except Payment.DoesNotExist:
                context['error'] = 'Payment record not found'
        
        return render(request, 'payments/failure.html', context)