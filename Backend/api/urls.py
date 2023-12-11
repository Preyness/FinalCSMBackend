from django.urls import path, include

urlpatterns = [
    path('accounts/', include('accounts.urls')),
    path('equipments/', include('equipments.urls')),
    path('transactions/', include('transactions.urls')),
    path('breakages/', include('breakages.urls')),
]
