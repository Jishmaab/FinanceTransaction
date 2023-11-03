from transaction import views
from django.urls import path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'contacts', views.ContactViewSet, basename='contact'),
router.register(r'transaction', views.TransactionViewSet, basename='transaction'),



urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
]+ router.urls    