from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import SocialClub, SocialClubImage
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from .forms import CreateSocialClubForm, SocialClubImageForm
from django.core.exceptions import PermissionDenied
from users.models import User


CLUB_PER_PAGE = 10
PAGE_PER_PAGE = 5
@login_required
def social_clubs(request):
    can_create_social_clubs = False
    if request.user.profile.ambassador or request.user.is_staff:
        can_create_social_clubs= True
    query = request.GET.get('q')
    if query:
        social_clubs = SocialClub.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    else:
        social_clubs = SocialClub.objects.all()
    social_clubs_attending = SocialClub.objects.filter(members=request.user)
    paginator = Paginator(social_clubs, CLUB_PER_PAGE)
    page = request.GET.get('page')
    social_clubs = paginator.get_page(page)
    

    return render(request, 'social_clubs/clubs.html', {'social_clubs': social_clubs, 'PAGE_PER_PAGE':PAGE_PER_PAGE,'social_clubs_attending': social_clubs_attending, "query":query, 'can_create_social_clubs':can_create_social_clubs})

club_PER_PAGE = 2
@login_required
def club_detail(request, pk):
    can_change = False
    club = get_object_or_404(SocialClub, pk=pk)
    images = club.social_club_images.all()
    all_attendants_list = club.members.all()
    is_attending = club.members.filter(id=request.user.id).exists()
    events = club.club_events.all()
    paginator = Paginator(events, club_PER_PAGE)
    page = request.GET.get('page')
    events = paginator.get_page(page)
    if request.user in club.managers.all() or request.user.is_staff:
        can_change = True
    if request.method == 'POST':
        if 'attend' in request.POST:
            club.members.add(request.user)
            messages.add_message(request,messages.constants.SUCCESS,f'You have successfully joined this group.')
            request.user.notifications.create(title=f'Joined The Club {club.name}', description="Check out the club!", url=reverse("club-detail", args=[club.pk]), club=club)

        elif 'unattend' in request.POST:
            club.members.remove(request.user)
            messages.add_message(request, messages.constants.SUCCESS, f'You have successfully unjoined this group.')
            request.user.notifications.create(title=f'Unjoined The Club {club.name}', description="Check out the club if you have changed your mind!!", url=reverse("club-detail", args=[club.pk]), club=club)

        return redirect("club-detail", pk=pk)


    
    return render(request, 'social_clubs/club_detail.html', {'club': club, 'events':events,'is_attending': is_attending, "shortened_attendant_list":all_attendants_list,'PAGE_PER_PAGE':PAGE_PER_PAGE, 'can_change':can_change,'images':images, 'exclude':['time','fee','location','description','from']})



@login_required
def create_club(request):
    if request.user.profile.ambassador or request.user.is_staff:
        if request.method == 'POST':
            form = CreateSocialClubForm(request.POST, user=request.user)
            image_form = SocialClubImageForm(request.POST)
            if form.is_valid():
                club = form.save(commit=False)
                club.save()
                club.members.add(request.user)
                club.managers.add(request.user)
                for staff_pk in [x.pk for x in User.objects.filter(is_staff=True)]:
                    club.managers.add(staff_pk)
                
                # Get the list of image IDs to keep
                add_images = request.POST.getlist('keep_image_add')
                # Save new images
                for image in request.FILES.getlist('images'):
                    if str(image) in add_images: 
                        SocialClubImage.objects.create(social_club=club, image=image)
                return redirect('club-detail', pk=club.pk)
                
        else:   
            form = CreateSocialClubForm(user=request.user)
            image_form = SocialClubImageForm(request.POST)
        return render(request, 'social_clubs/create_club.html', {'form': form, 'image_form':image_form})
    else:
        raise PermissionDenied()
       

@login_required
def edit_club(request, pk):
    club = SocialClub.objects.get(pk=pk)
    if request.user in club.managers.all() or request.user.is_staff:
        if request.method == 'POST':
            image_form = SocialClubImageForm(request.POST, instance=club)
            form = CreateSocialClubForm(request.POST,instance=club, user=request.user)
            if form.is_valid():
                form.save()

                 # Get the list of image IDs to keep
                add_images = request.POST.getlist('keep_image_add')
                

                # Delete the images that were unchecked
                no_delete_images = request.POST.getlist('no_delete_image')
                
                
                # Look for all of the images' id's, delete the ones that do not appear in no_delete_images.
                to_delete = [x.id for x in club.social_club_images.all()]
                
                for image_id in to_delete:
                    if str(image_id) not in no_delete_images:
                        image = club.social_club_images.get(id=image_id)
                        image.delete()
                
                # Save new images
                for image in request.FILES.getlist('images'):
                    if str(image) in add_images: 
                        SocialClubImage.objects.create(social_club=club, image=image)
                return redirect('club-detail', pk=club.pk)

        else:
            form = CreateSocialClubForm(instance=club, user=request.user)
            image_form = SocialClubImageForm(instance=club)
           
        return render(request, 'social_clubs/edit_club.html', {'form':form,'image_form':image_form})
    else:
        raise PermissionDenied()


@login_required
def delete_club(request, pk):
    club = get_object_or_404(SocialClub, pk=pk)
    club_title = club.name
    if request.user in club.managers.all() or request.user.is_staff:
        request.user.notifications.create(title=f'You have deleted the club {club_title}', description="You have deleted a club!")
        if request.method == 'POST':
            club.delete()
        messages.add_message(request, messages.constants.SUCCESS, "Club deleted!")
        return redirect('social-clubs')
    else:
        raise PermissionDenied()

