from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import SocialClub
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q


CLUB_PER_PAGE = 10
PAGE_PER_PAGE = 5
@login_required
def social_clubs(request):
    social_clubs = SocialClub.objects.all()
    social_clubs_attending = SocialClub.objects.filter(members=request.user)
    paginator = Paginator(social_clubs, CLUB_PER_PAGE)
    page = request.GET.get('page')
    social_clubs = paginator.get_page(page)
    return render(request, 'social_clubs/clubs.html', {"social_clubs":social_clubs,"social_clubs_attending":social_clubs_attending,'PAGE_PER_PAGE':PAGE_PER_PAGE})

@login_required
def search_clubs(request):
    query = request.GET.get('q')
    if query:
        social_clubs = SocialClub.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    else:
        social_clubs = SocialClub.objects.none()
    print(social_clubs)
    social_clubs_attending = SocialClub.objects.filter(members=request.user)
    paginator = Paginator(social_clubs, CLUB_PER_PAGE)
    page = request.GET.get('page')
    social_clubs = paginator.get_page(page)
    

    return render(request, 'social_clubs/search_clubs.html', {'social_clubs': social_clubs, 'PAGE_PER_PAGE':PAGE_PER_PAGE,'social_clubs_attending': social_clubs_attending, "query":query})



EVENT_PER_PAGE = 2
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

