import razorpay
from django.conf import settings
from decimal import Decimal
import logging
import requests.exceptions
import socket

logger = logging.getLogger(__name__)

class RazorpayService:
    def __init__(self):
        if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
            raise Exception("Razorpay credentials are not properly configured")
            
        try:
            self.client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )
            
            # Skip validation in development if network issues
            if not settings.DEBUG:
                try:
                    self.client.order.all()
                except (requests.exceptions.ConnectionError, 
                       socket.gaierror, 
                       requests.exceptions.RequestException) as e:
                    logger.warning(f"Network error during Razorpay initialization: {str(e)}")
                    # Continue anyway in development
                except razorpay.errors.BadRequestError as e:
                    logger.error(f"Razorpay authentication failed: {str(e)}")
                    raise Exception("Invalid Razorpay API credentials")
                    
        except Exception as e:
            logger.error(f"Razorpay initialization error: {str(e)}")
            if settings.DEBUG:
                logger.warning("Continuing despite Razorpay initialization error (DEBUG mode)")
            else:
                raise Exception(f"Failed to initialize Razorpay client: {str(e)}")

    def create_order(self, amount, currency='INR'):
        """Create Razorpay Order"""
        try:
            # Convert amount to paise
            amount_in_paise = int(Decimal(str(amount)) * 100)
            
            data = {
                'amount': amount_in_paise,
                'currency': currency,
                'payment_capture': '1'
            }
            
            order = self.client.order.create(data=data)
            logger.info(f"Razorpay order created successfully: {order['id']}")
            return order
            
        except (requests.exceptions.ConnectionError, socket.gaierror) as e:
            logger.error(f"Network error during order creation: {str(e)}")
            raise Exception("Network error: Unable to connect to Razorpay")
        except razorpay.errors.BadRequestError as e:
            logger.error(f"Razorpay order creation failed: {str(e)}")
            raise Exception(f"Razorpay Bad Request: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during order creation: {str(e)}")
            raise Exception(f"Order creation failed: {str(e)}")

    def verify_payment_signature(self, payment_id, order_id, signature):
        """Verify Razorpay payment signature"""
        try:
            self.client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })
            return True
        except razorpay.errors.SignatureVerificationError:
            return False

