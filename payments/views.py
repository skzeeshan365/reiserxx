import stripe as stripe
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from djangoProject1 import settings
from payments.forms import DonationForm


# Create your views here.

def home(request):
    form = DonationForm()
    return render(request, 'Payments/home.html', {'form': form})


def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)


@csrf_exempt
def create_checkout_session(request):
    if request.method == 'GET':
        domain_url = 'http://127.0.0.1:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:

            checkout_session = stripe.checkout.Session.create(
                api_key=stripe.api_key,
                success_url=domain_url + 'payments/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + 'payments/cancelled/',
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': 'Your Product Name',
                            },
                            'unit_amount': 10000,  # Amount in cents
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})


@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # This method will be called when user successfully purchases something.
        handle_checkout_session(session)

    return HttpResponse(status=200)


def handle_checkout_session(session):
    # client_reference_id = user's id
    client_reference_id = session.get("client_reference_id")
    payment_intent = session.get("payment_intent")

    if client_reference_id is None:
        # Customer wasn't logged in when purchasing
        return

    # Customer was logged in we can now fetch the Django user and make changes to our models
    try:
        user = User.objects.get(id=client_reference_id)
        print(user.username, "just purchased something.")


    except User.DoesNotExist:
        pass


class SuccessView(TemplateView):
    template_name = 'Payments/success.html'


class CancelledView(TemplateView):
    template_name = 'Payments/cancelled.html'