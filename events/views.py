from .models import Event
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .forms import CreateEventForm
from django.core.exceptions import PermissionDenied
from django.contrib import messages


EVENT_PER_PAGE = 10
PAGE_PER_PAGE = 5



@login_required
def events(request):
    events = Event.objects.all()
    events_attending = Event.objects.filter(users=request.user)
    paginator = Paginator(events, EVENT_PER_PAGE)
    page = request.GET.get('page')
    events = paginator.get_page(page)

    return render(request, 'events/events.html', {'events': events, 'PAGE_PER_PAGE':PAGE_PER_PAGE,'events_attending': events_attending})

@login_required
def my_events(request):
    # Get the current user's events they are attending
    events = Event.objects.filter(users=request.user)
    events_attending = Event.objects.filter(users=request.user)
    paginator = Paginator(events, EVENT_PER_PAGE)
    page = request.GET.get('page')
    events = paginator.get_page(page)
    return render(request, 'events/my_events.html', {'events': events, 'PAGE_PER_PAGE':PAGE_PER_PAGE,'events_attending': events_attending})

def event_detail(request, pk):
    event = Event.objects.get(pk=pk)
    all_attendants_list = event.users.all()[:5]
    is_attending = event.users.filter(id=request.user.id).exists()
    if request.method == 'POST':
        if 'attend' in request.POST:
            event.users.add(request.user)
        elif 'unattend' in request.POST:
            event.users.remove(request.user)
        return redirect("event-detail", pk=pk)

    return render(request, 'events/event_detail.html', {'event': event, 'is_attending': is_attending, "shortened_attendant_list":all_attendants_list})

@login_required
def create_event(request):
    if request.method == 'POST':
        form = CreateEventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            event.users.add(request.user)
            
            
            return redirect('event-detail', pk=event.pk)
    else:
        form = CreateEventForm()
    return render(request, 'events/create_event.html', {'form': form})

@login_required
def delete_event(request, pk):
    
    event = get_object_or_404(Event, pk=pk)
    if request.user.pk != event.created_by.pk:
        raise PermissionDenied("You can't edit this profile!")

    if request.method == 'POST':
        event.delete()
    messages.add_message(request, messages.constants.ERROR, "Event deleted!")
    return redirect('events')