from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse

from .models import Airport, Flight, Passenger

import logging

# Create your views here.
def index(request):
    #return HttpResponse("hello flights !")
    return render(request, "flights/index.html", {
       "flights" : Flight.objects.all() 
    })

# def flight (request, flight_id):
#    flight = Flight.objects.get(pk=flight_id)
#    return render(request, "flights/flight.html", {
#        "flight" : flight ,
#        "passengers": flight.passengers.all(),
#        #"non_passengers": Passenger.objects.exclude(flight.passengers.all())
#        "non_passengers": Passenger.objects.exclude(flights=flight).all()
#     })

def flight(request, flight_id):
    try:
        flight = Flight.objects.get(id=flight_id)
    except Flight.DoesNotExist:
        raise Http404("Flight not found.")
    return render(request, "flights/flight.html", {
        "flight": flight,
        "passengers": flight.passengers.all(),
        "non_passengers": Passenger.objects.exclude(flights=flight).all()
    })


def book (request, flight_id):
    if request.method == "POST":
        
        #logger = logging.getLogger(__name__)
        #logger.info('This is an info message')
        flight = Flight.objects.get(pk = flight_id)
        passenger = Passenger.objects.get(pk = int(request.POST["passenger"])) 
        flight.passengers.add(passenger)
        return HttpResponseRedirect(reverse("flight", args=(flight_id,))) # reverse construct url based on defined routs




