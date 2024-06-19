from django.shortcuts import render
from django.views import View
from django.views.generic import DetailView, ListView
from .models import Price, Product
import stripe
from django.conf import settings
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView
stripe.api_key = settings.STRIPE_SECRET_KEY




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
