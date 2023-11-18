# myapp/views.py
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import stripe
import json
import logging

stripe.api_key = 'sk_test_51ODhd6B9sAFUoYRFTTpBxMsoTOwRTkAjN388O4hvpOMu6iSJt0Qs3KjjNkUymQ1hotAhZgMwMf1xeZt3Gf7bMcte0075yPbvYt'

# Set up logging
logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def create_checkout_session(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        # Log the custom_amount for debugging

        custom_amount = data.get('amount')

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Total',
                    },
                    # Convert to cents
                    'unit_amount': int(custom_amount * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            # Use the current domain for success
            success_url='http://localhost:3000/checkout?success=true',
            # Use the current domain for cancel
            cancel_url='http://localhost:3000/checkout'
        )

        # Retrieve the session ID from the created Checkout Session and include it in the response
        session_id = session.id
        return JsonResponse({'client_secret': session.client_secret, 'sessionId': session_id})

    except Exception as e:
        # Log the error for debugging purposes
        logger.exception("Error creating Checkout Session:")
        return JsonResponse({'error': str(e)}, status=500)
