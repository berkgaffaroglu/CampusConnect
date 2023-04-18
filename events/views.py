from .models import Event
from django.db.models import Q
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .forms import CreateEventForm
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from .forms import CreateEventForm
from .models import SocialClub

EVENT_PER_PAGE = 10
PAGE_PER_PAGE = 5

# This function checks if the current user is a manager in any of the social clubs.
def check_if_manager(user):
    managing_clubs = user.admin_of.all()
    if len(managing_clubs) > 0 or user.is_staff:
        return True
    else:
        return False

@login_required
def events(request):
    query = request.GET.get('q')
    if query:
        events = Event.objects.filter(Q(title__icontains=query) | Q(created_by__username__icontains=query)).order_by('-time')
    else:
        events = Event.objects.all()
    events_attending = Event.objects.filter(users=request.user)
    paginator = Paginator(events, EVENT_PER_PAGE)
    page = request.GET.get('page')
    events = paginator.get_page(page)
    manager = check_if_manager(request.user)

    return render(request, 'events/events.html', {'events': events, 'PAGE_PER_PAGE':PAGE_PER_PAGE,'events_attending': events_attending, "query":query, "manager":manager})

def event_detail(request, pk):
    can_change = False
    event = Event.objects.get(pk=pk)
    all_attendants_list = event.users.all()
    is_attending = event.users.filter(id=request.user.id).exists()
    # This if statement is checking if the user is capable of editing the current event. To be able to edit,
    # user has to be either from the staff or the manager of the club that posted the event.
    if request.user in event.social_club.managers.all() or request.user.is_staff: 
        can_change = True
    if request.method == 'POST':
        if 'attend' in request.POST:
            event.users.add(request.user)
            messages.add_message(request,messages.constants.SUCCESS,f'You have successfully attended to the event')
        elif 'unattend' in request.POST:
            event.users.remove(request.user)
            messages.add_message(request, messages.constants.SUCCESS, f'You have successfully unattended to the event')
        return redirect("event-detail", pk=pk)

    return render(request, 'events/event_detail.html', {'event': event, 'is_attending': is_attending, "shortened_attendant_list":all_attendants_list, 'can_change':can_change })

@login_required
def create_event(request):
    # If the current user is not a manager at any social club, raise a permission error.
    if not check_if_manager(request.user):
        raise PermissionDenied()
    
    if request.method == 'POST':
        form = CreateEventForm(request.POST, user=request.user)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            event.users.add(request.user)
            return redirect('event-detail', pk=event.pk)
    else:
        form = CreateEventForm(user=request.user)
    return render(request, 'events/create_event.html', {'form': form})

@login_required
def edit_event(request, pk):
    # If the current user is not a manager at any social club, raise a permission error.
    if not check_if_manager(request.user):
        raise PermissionDenied()
    event = Event.objects.get(pk=pk)
    if request.user in event.social_club.managers.all() or request.user.is_staff: 
        if request.method == 'POST':
            
            form = CreateEventForm(request.POST,instance=event, user=request.user)
            if form.is_valid():
                form.save()
                return redirect('event-detail', pk=event.pk)

        else:
            form = CreateEventForm(instance=event, user=request.user)

        return render(request, 'events/edit_event.html', {'form':form})


@login_required
def delete_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if not request.user in event.social_club.managers.all() or not request.user.is_staff: 
        raise PermissionDenied()
    else:
        if request.method == 'POST':
            event.delete()
        messages.add_message(request, messages.constants.ERROR, "Event deleted!")
        return redirect('events')

