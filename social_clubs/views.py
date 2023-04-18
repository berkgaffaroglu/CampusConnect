from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import SocialClub
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from .forms import CreateSocialClubForm
from django.core.exceptions import PermissionDenied


CLUB_PER_PAGE = 10
PAGE_PER_PAGE = 5
@login_required
def social_clubs(request):
    query = request.GET.get('q')
    if query:
        social_clubs = SocialClub.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    else:
        social_clubs = SocialClub.objects.all()
    social_clubs_attending = SocialClub.objects.filter(members=request.user)
    paginator = Paginator(social_clubs, CLUB_PER_PAGE)
    page = request.GET.get('page')
    social_clubs = paginator.get_page(page)
    

    return render(request, 'social_clubs/clubs.html', {'social_clubs': social_clubs, 'PAGE_PER_PAGE':PAGE_PER_PAGE,'social_clubs_attending': social_clubs_attending, "query":query})

club_PER_PAGE = 2
@login_required
def club_detail(request, pk):
    can_change = False
    club = get_object_or_404(SocialClub, pk=pk)
    all_attendants_list = club.members.all()
    is_attending = club.members.filter(id=request.user.id).exists()
    clubs = club.club_events.all()
    paginator = Paginator(clubs, club_PER_PAGE)
    page = request.GET.get('page')
    clubs = paginator.get_page(page)
    if request.user in club.managers.all() or request.user.is_staff:
        can_change = True
    if request.method == 'POST':
        if 'attend' in request.POST:
            club.members.add(request.user)
            messages.add_message(request,messages.constants.SUCCESS,f'You have successfully joined this group.')
        elif 'unattend' in request.POST:
            club.members.remove(request.user)
            messages.add_message(request, messages.constants.SUCCESS, f'You have successfully unjoined this group.')
        return redirect("club-detail", pk=pk)

    return render(request, 'social_clubs/club_detail.html', {'club': club, 'clubs':clubs,'is_attending': is_attending, "shortened_attendant_list":all_attendants_list,'PAGE_PER_PAGE':PAGE_PER_PAGE, 'can_change':can_change})



@login_required
def create_club(request):
    if request.user.profile.ambassador or request.user.is_staff:
        if request.method == 'POST':
            form = CreateSocialClubForm(request.POST, user=request.user)
            if form.is_valid():
                club = form.save(commit=False)
                club.save()
                club.members.add(request.user)
                club.managers.add(request.user)
                
                
                return redirect('club-detail', pk=club.pk)
        else:   
            form = CreateSocialClubForm(user=request.user)
        return render(request, 'social_clubs/create_club.html', {'form': form})
    else:
        raise PermissionDenied()
       

@login_required
def edit_club(request, pk):
    club = SocialClub.objects.get(pk=pk)
    if request.user in club.managers.all() or request.user.is_staff:
        if request.method == 'POST':
            
            form = CreateSocialClubForm(request.POST,instance=club, user=request.user)
            if form.is_valid():
                form.save()
                return redirect('club-detail', pk=club.pk)

        else:
            form = CreateSocialClubForm(instance=club, user=request.user)

        return render(request, 'social_clubs/edit_club.html', {'form':form})
    else:
        raise PermissionDenied()


@login_required
def delete_club(request, pk):
    club = get_object_or_404(SocialClub, pk=pk)
    if request.user in club.managers.all() or request.user.is_staff:
        if request.method == 'POST':
            club.delete()
        messages.add_message(request, messages.constants.ERROR, "Club deleted!")
        return redirect('social-clubs')
    else:
        raise PermissionDenied()

