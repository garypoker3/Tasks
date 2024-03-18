from django.urls import path
from . import views

urlpatterns = [
    path("process-file/", views.process_file, name="process_file"),
    path("apply-conversion/", views.apply_conversion, name="apply_conversion"),
]
