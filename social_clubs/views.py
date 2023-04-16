from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import SocialClub
from django.core.paginator import Paginator
from django.contrib import messages


CLUB_PER_PAGE = 10
PAGE_PER_PAGE = 5
@login_required
def socail_clubs(request):
    social_clubs = SocialClub.objects.all()
    paginator = Paginator(social_clubs, CLUB_PER_PAGE)
    page = request.GET.get('page')
    social_clubs = paginator.get_page(page)
    return render(request, 'social_clubs/clubs.html', {"social_clubs":social_clubs, 'paginator':paginator})

@login_required
def club_detail(request, pk):
    club = SocialClub.objects.get(pk=pk)
    all_attendants_list = club.users.all()
    is_attending = club.users.filter(id=request.user.id).exists()
    if request.method == 'POST':
        if 'attend' in request.POST:
            club.users.add(request.user)
            messages.add_message(request,messages.constants.SUCCESS,f'You have successfully joined this group.')
        elif 'unattend' in request.POST:
            club.users.remove(request.user)
            messages.add_message(request, messages.constants.SUCCESS, f'You have successfully unjoined this group.')
        return redirect("club-detail", pk=pk)

    return render(request, 'clubs/club_detail.html', {'club': club, 'is_attending': is_attending, "shortened_attendant_list":all_attendants_list})