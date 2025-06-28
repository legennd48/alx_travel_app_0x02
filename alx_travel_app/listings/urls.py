from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import (
    ListingViewSet, 
    BookingViewSet, 
    PaymentViewSet,
    PaymentSuccessView,
    PaymentCallbackView,
    PaymentFailureView
)

router = DefaultRouter()
router.register(r'listings', ListingViewSet, basename='listing')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'payments', PaymentViewSet, basename='payment')

# Additional URL patterns for payment handling
urlpatterns = [
    # Payment success page (where users are redirected after successful payment)
    path('payment-success/', PaymentSuccessView.as_view(), name='payment-success'),
    
    # Payment callback endpoint (Chapa sends POST requests here)
    path('api/payments/callback/', PaymentCallbackView.as_view(), name='payment-callback'),
    
    # Payment failure page (where users are redirected after failed payment)
    path('payment-failure/', PaymentFailureView.as_view(), name='payment-failure'),
] + router.urls