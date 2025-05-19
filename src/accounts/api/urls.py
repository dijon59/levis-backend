from src.accounts.api import views 
from src.electric_app.routers import api


apis = [
    api(r'register', views.RegisterViewset, name='register'),
    api(r'login', views.LoginAPIView, name='login'),
    api(r'team', views.TeamViewset, name='team'),
    api(r'customer', views.CustomerViewset, name='customer'),
    api(r'register-device', views.RegisterDeviceViewset, name='register-device'),
]
