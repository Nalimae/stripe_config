from django.shortcuts import render
from django.views import View
from django.views.generic import DetailView, ListView
from .models import Price, Product
import stripe
from django.conf import settings
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

stripe.api_key = settings.STRIPE_SECRET_KEY


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    """
    Stripe webhook view to hadle checkout session completed event.
    """

    def post(self, request, format=None):
        payload=request.body
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        sig_header= request.META["HTTP_STRIPE_SIGNATURE"]
        event = None

        try:
            event =stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            #Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            #Invalid signature
            return HttpResponse(status=400)
        
        if event["type"] == "checkout.session.completed":
            print("Payment successful")

            session = event["data"]["object"]
            customer_email = session["customer_details"]["email"]
            product_id = session["metadata"]["product_id"]
            product = get_object_or_404(Product, id=product_id)

            send_mail(
                subject = "Here is your product",
                message=f"Thanks for your purchase. The URL is : {product.url}",
                recipient_list=[customer_email],
                from_email="musauldennis@gmail.com",
            )

            # can handle other events here
        return HttpResponse(status=200)


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    """ Stripe webhook to handle checkout session"""

    def post(self, request, format=None):
        payload = request.body
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        event = None

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            #invalid signature
            return HttpResponse(status=400)
        
        if event["type"] == "checkout.session.completed":
            print("Payment successful")
            session =  event["data"]["object"]
            customer_email= session["customer_details"]["email"]
            product_id = session["metatada"]["product_id"]
            product = get_object_or_404(Product, id=product_id)


            send_mail(
                subject="Here is your product",
                message=f"Thanks for your purchase. The URL is: {product.url}",
                recipient_list=[customer_email],
                from_email="test@gmail.com",
            )

            PaymentHistory.objects.create(
                email=customer_email, product=product, payment_status="completed"
            ) # Add this

        # Can handle other events here.

        return HttpResponse(status=200)





class CreateStripeCheckoutSessionView(View):
    """
    create a checkput session and redirect the user to a stripe checkout
    """
    def post (self,request, *args, **kwargs):
        price =Price.objects.get(id=self.kwargs["pk"])
        checkout_session=stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items = [
                {

                    "price_data":{
                        "currency":"usd",
                        "unit_amount":int(price.price) * 100,
                        "product_data":{
                            "name": price.product.name,
                            "description":price.product.desc,
                            "images":[
                                f"{settings.BACKEND_DOMAIN}/{price.product.thumbnail}"
                            ],

                        },
                    },
                    "quantity":price.product.quantity,

                }
            ],
            metadata={"product_id":price.product.id},
            mode="payment",
            success_url=settings.PAYMENT_SUCCESS_URL,
            cancel_url=settings.PAYMENT_CANCEL_URL,
        )

        return redirect(checkout_session.url)

# sucess class
class SuccessView(TemplateView):
    template_name = "products/success.html"

class CancelView(TemplateView):
    template_name = "products/cancel.html"

# Create your views here.
class ProductListView(ListView):
    model = Product
    context_object_name ="products"
    template_name = "products/product_list.html"

class ProductDetailView(DetailView):
    model =  Product
    context_object_name = "product"
    template_name = "products/product_detail.html"

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data()
        context["prices"] = Price.objects.filter(product=self.get_object())
        return context
