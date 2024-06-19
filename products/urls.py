from django.urls import include, path
from .views import *

app_name = "products"


urlpatterns = [

    path("",ProductListView.as_view(), name="product-list"),
    path("<int:pk>/",ProductDetailView.as_view(), name="product-detail"),
    path("create-checkout-session/<int:pk>/", CreateStripeCheckoutSessionView.as_view(),
         name="create-checkout-session",),
    path("success/", SuccessView.as_view(), name="success"),
    path("cancel/", CancelView.as_view(), name="cancel"),

    
]