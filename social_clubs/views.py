from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import SocialClub
from django.core.paginator import Paginator
from django.contrib import messages


CLUB_PER_PAGE = 10
PAGE_PER_PAGE = 5
@login_required
def social_clubs(request):
    social_clubs = SocialClub.objects.all()
    social_clubs_attending = SocialClub.objects.filter(members=request.user)
    paginator = Paginator(social_clubs, CLUB_PER_PAGE)
    page = request.GET.get('page')
    social_clubs = paginator.get_page(page)
    return render(request, 'social_clubs/clubs.html', {"social_clubs":social_clubs,"social_clubs_attending":social_clubs_attending, 'paginator':paginator,'PAGE_PER_PAGE':PAGE_PER_PAGE})

EVENT_PER_PAGE = 10
@login_required
def club_detail(request, pk):
    club = SocialClub.objects.get(pk=pk)

    all_attendants_list = club.members.all()
    is_attending = club.members.filter(id=request.user.id).exists()
    events = club.club_events.all()
    paginator = Paginator(events, EVENT_PER_PAGE)
    page = request.GET.get('page')
    events = paginator.get_page(page)
    if request.method == 'POST':
        if 'attend' in request.POST:
            club.members.add(request.user)
            messages.add_message(request,messages.constants.SUCCESS,f'You have successfully joined this group.')
        elif 'unattend' in request.POST:
            club.members.remove(request.user)
            messages.add_message(request, messages.constants.SUCCESS, f'You have successfully unjoined this group.')
        return redirect("club-detail", pk=pk)

    return render(request, 'social_clubs/club_detail.html', {'club': club, 'events':events,'is_attending': is_attending, "shortened_attendant_list":all_attendants_list,'PAGE_PER_PAGE':PAGE_PER_PAGE})