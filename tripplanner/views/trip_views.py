from django.urls import reverse_lazy
from django.db import transaction
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic import ListView, DetailView
from tripplanner.decorators import user_is_admin_or_trip_creator, user_is_trip_participant
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from tripplanner.forms import *
from tripplanner import models
from django.contrib.auth.models import User
from django.http import JsonResponse

# import pdfkit
# from django.http import HttpResponse

group1 = [login_required, user_is_admin_or_trip_creator]
group2 = [login_required, user_is_trip_participant]


class TripList(ListView):
    model = Trip

    def get_queryset(self): #todo: chenage display filters for diff users
        curr_user = User.objects.get(pk=self.request.user.id)
        if not curr_user.is_superuser:
            return Trip.objects.filter(created_by=self.request.user.pk)
        else:
            return Trip.objects.all()


@method_decorator(group2, name='dispatch')
class TripDetail(DetailView):
    model = Trip


@method_decorator(login_required, name='dispatch')
class TripWithAttributesCreate(CreateView):
    model = Trip
    form_class = TripForm
    template_name_suffix = '_with_attributes_form'

    def get_context_data(self, **kwargs):
        data = super(TripWithAttributesCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['journeys'] = JourneyFormSet(self.request.POST, ) # todo: ta czesc w create niepotrzebna ?
            data['accommodations'] = AccommodationFormSet(self.request.POST)
            data['attractions'] = AttractionFormSet(self.request.POST)
        else:
            data['journeys'] = JourneyFormSet()
            data['accommodations'] = AccommodationFormSet()
            data['attractions'] = AttractionFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        journeys = context['journeys']
        accommodations = context['accommodations']
        attractions = context['attractions']
        with transaction.atomic():
            if attractions.is_valid() and accommodations.is_valid() and journeys.is_valid():
                current_user = self.request.user
                form.instance.created_by = current_user
                self.object = form.save()
                self.object.participants.add(current_user)

                if journeys.is_valid():
                    journeys.instance = self.object
                    journeys.save()
                if accommodations.is_valid():
                    accommodations.instance = self.object
                    accommodations.save()
                if attractions.is_valid():
                    attractions.instance = self.object
                    attractions.save()
                models.Trip.update_dates_and_price(self.object, journeys.cleaned_data, accommodations.cleaned_data,
                                                   attractions.cleaned_data)
            else:
                return self.form_invalid(form)

        return super(TripWithAttributesCreate, self).form_valid(form)


@method_decorator(group1, name='dispatch')
class TripWithAttributesUpdate(UpdateView):
    model = Trip
    form_class = TripForm
    template_name_suffix = '_with_attributes_form'

    def get_context_data(self, **kwargs):
        data = super(TripWithAttributesUpdate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['journeys'] = JourneyFormSet(self.request.POST, instance=self.object)
            data['accommodations'] = AccommodationFormSet(self.request.POST, instance=self.object)
            data['attractions'] = AttractionFormSet(self.request.POST, instance=self.object)
        else:
            data['journeys'] = JourneyFormSet(instance=self.object)
            data['accommodations'] = AccommodationFormSet(instance=self.object)
            data['attractions'] = AttractionFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        journeys = context['journeys']
        accommodations = context['accommodations']
        attractions = context['attractions']
        with transaction.atomic():
            if attractions.is_valid() and accommodations.is_valid() and journeys.is_valid():
                form.instance.created_by = self.request.user
                self.object = form.save()

                if journeys.is_valid():
                    journeys.instance = self.object
                    journeys.save()
                if accommodations.is_valid():
                    accommodations.instance = self.object
                    accommodations.save()
                if attractions.is_valid():
                    attractions.instance = self.object
                    attractions.save()
                models.Trip.update_dates_and_price(self.object, journeys.cleaned_data, accommodations.cleaned_data,
                                                   attractions.cleaned_data)
            else:
                return self.form_invalid(form)

        return super(TripWithAttributesUpdate, self).form_valid(form)


@method_decorator(group1, name='dispatch')
class TripDelete(DeleteView):
    model = Trip
    success_url = reverse_lazy('trip-list')

@method_decorator(login_required, name='dispatch')
class TripParticipantsList(FormView):
    form_class = AddParticipantForm
    template_name = 'tripplanner/trip_participants_list.html'

    def get_success_url(self):
        return reverse_lazy('trip-participants', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        data = super(TripParticipantsList, self).get_context_data(**kwargs)
        data['participants'] = Trip.objects.get(id=self.kwargs['pk']).participants.all()
        data['trip_name'] = Trip.objects.get(id=self.kwargs['pk']).name
        data['trip_creator'] = Trip.objects.get(id=self.kwargs['pk']).created_by_id
        return data

    def form_valid(self, form):
        trip = Trip.objects.get(id=self.kwargs['pk'])
        user = User.objects.filter(username__iexact=form.cleaned_data['username']).first()
        trip.participants.add(user)

        return super(TripParticipantsList, self).form_valid(form)

def validate_participant(request):
    username = request.GET.get('username', None)
    trip_name = request.GET.get('tripName', None)
    trip = Trip.objects.filter(name=trip_name).first()
    success = False
    if User.objects.filter(username__iexact=username).exists():
        if username not in list(trip.participants.values_list('username', flat=True).all()):
            success = True

    data = {
        'exists': success,
        'message_error' : "User doesn't exist or is already added.",
        'message_text' : 'Click "add" to add this user to your trip.'
    }
    return JsonResponse(data)
#
# def pdffile(request):
#
#     # pdf = pdfkit.from_url("http://localhost:8001/trip/1/", "trip1.pdf")
#     # return HttpResponse("Everything working good, check out the root of your project to see the generated PDF.")
#
#     # Use False instead of output path to save pdf to a variable
#     pdf = pdfkit.from_url('http://localhost:8001/tripplanner/published-trip', False)
#     response = HttpResponse(pdf,content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="trip1.pdf"'
#
#
#     return response
