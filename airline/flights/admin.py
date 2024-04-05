from django.contrib import admin

from .models import Airport, Flight, Passenger

class FlightAdmin(admin.ModelAdmin):
    list_display = ("id", "origin", "destination", "duration")

class PassengerSettings(admin.ModelAdmin):
    filter_horizontal = ("flights", )    

# Register your models here.
admin.site.register(Airport)
admin.site.register(Flight, FlightAdmin)
admin.site.register(Passenger, PassengerSettings)
