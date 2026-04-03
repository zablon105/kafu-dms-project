from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Connect documents app
    path('', include('documents.urls')),
]