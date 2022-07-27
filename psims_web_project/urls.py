from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include, re_path
from psims.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', login_required(FormWizardView.as_view())),
    path('api/check-status/', check_worker_status),
    path('activate/<str:uidb64>/<str:token>/', activate, name='activate'),
    path('final_activate/<str:uidb64>/<str:token>/', final_activate, name='final_activate'),
    path('<str:username>/results/<int:id>/', result, name="result"),
    path('<str:username>/results/', results_list, name='results'),
    path('<str:username>/results/<int:id>/risk/', risk),
    path('<str:username>/wizard_view/', end_wizard_view, name='wizard_view'),
    path('cards/', choice_card, name='cards'),
    path("logout/", logout_view, name="logout"),       
    path('cancel/', login_required(CancelView.as_view()), name='cancel'),
    path('success/', login_required(SuccessView.as_view()), name='success'),
    path('landing/', login_required(ProductLandingPageView.as_view()), name='landing'),
    path('create-checkout-session/<pk>/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('webhooks/stripe/', stripe_webhook, name='stripe-webhook'),
    path('create-payment-intent/<pk>/', StripeIntentView.as_view(), name='create-payment-intent'),
    # path('<str:username>/chart', views.chart),  #Live Yield URL
    path('my_account/', my_account, name="my_account"),
    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    # path("", include("authentication.urls")),  # Auth routes - login / register
    # path("", include("app.urls"))  # UI Kits Html files
    # The home page
    path('home/', index, name='home'),
    # Matches any html file
    re_path(r'^.*""', pages, name='pages'),
    #TODO: revisit
    # path('app/', views.index, name='main-view'),
    # path('app/crop/', views.crop, name='crop-view'),
]

urlpatterns += staticfiles_urlpatterns()

""" deleting all the working functions from the db """
try:
    PsimsUser.objects.all().delete()
except:
    pass