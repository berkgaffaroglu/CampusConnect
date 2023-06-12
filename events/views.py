from .models import Event, EventImage, EventComment, EventHeart
from django.db.models import Q,Count
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .forms import CreateEventForm, EventImageForm
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from .forms import CreateEventForm
from .models import SocialClub
from users.models import User
from django.http import HttpResponse


EVENT_PER_PAGE = 10
PAGE_PER_PAGE = 5

# This function checks if the current user is a manager in any of the social clubs.
def check_if_manager(user):
    managing_clubs = user.admin_of.all()
    if len(managing_clubs) > 0 or user.is_staff:
        return True
    else:
        return False
    
def is_past(self):
    if self.time < timezone.now():
        return True
    else:
        return False
    
@login_required
def events(request):
    try:
        query = request.GET.get('q').split('&')[0]
        search=True
    except AttributeError:
        query = request.GET.get('q')

    if query:
        events = Event.objects.filter(Q(title__icontains=query) | Q(social_club__name__icontains=query)).annotate(is_attending=Count('users', filter=Q(users=request.user))) \
            .annotate(is_liked=Count('likes_event', filter=Q(likes_event__user=request.user))) \
            .order_by('-is_liked', '-is_attending', '-created_time')
    else:
        search = False
        social_clubs = request.user.clubs_joined.all()
        events = Event.objects.filter(social_club__in=social_clubs) \
            .exclude(pk__in=request.user.profile.dont_recommend_events.all()) \
            .annotate(is_attending=Count('users', filter=Q(users=request.user))) \
            .annotate(is_liked=Count('likes_event', filter=Q(likes_event__user=request.user))) \
            .order_by('-is_liked', '-is_attending', '-created_time')
            
        non_past_events = []
        for event in events:
            if not is_past(event):
                non_past_events.append(event)
        events = non_past_events

    events_attending = Event.objects.filter(users=request.user)
    paginator = Paginator(events, EVENT_PER_PAGE)
    page = request.GET.get('page')
    events = paginator.get_page(page)
    manager = check_if_manager(request.user)

    if request.method == 'POST':
        if 'dont_recommend' in request.POST:
            event_pk = request.POST['event_pk']
            request.user.profile.dont_recommend_events.add(Event.objects.get(pk=event_pk))
            request.user.profile.save()
            messages.add_message(request,messages.constants.SUCCESS,f"The event {Event.objects.get(pk=event_pk).title} won't be recommended to you again. Go to your profile and click to Dont Recommend Events if you change your mind.")
    

    return render(request, 'events/events.html', {'events': events, 'PAGE_PER_PAGE':PAGE_PER_PAGE,'events_attending': events_attending, "query":query, "manager":manager, "search":search, 'exclude':['fee','location','description','time']})


@login_required
def liked_events(request, pk):
    events = get_object_or_404(User, pk=pk).profile.liked_events().order_by('-created_time')
    events_attending = Event.objects.filter(users=request.user)
    paginator = Paginator(events, EVENT_PER_PAGE)
    page = request.GET.get('page')
    events = paginator.get_page(page)
    manager = check_if_manager(request.user)
    user = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        if 'dont_recommend' in request.POST:
            event_pk = request.POST['event_pk']
            request.user.profile.dont_recommend_events.add(Event.objects.get(pk=event_pk))
            request.user.profile.save()
            messages.add_message(request,messages.constants.SUCCESS,f"The event {Event.objects.get(pk=event_pk).title} won't be recommended to you again. Go to your profile and clear your 'Dont Recommend List' if you change your mind!")
        return redirect("events")

    return render(request, 'events/liked_events.html', {'events': events, 'PAGE_PER_PAGE':PAGE_PER_PAGE,'events_attending': events_attending, "manager":manager,"user":user, 'exclude':['fee','location','description','time']})

@login_required
def dont_recommend_events(request, pk):
    events = get_object_or_404(User, pk=pk).profile.dont_recommend_events.all().order_by('-created_time')
    events_attending = Event.objects.filter(users=request.user)
    paginator = Paginator(events, EVENT_PER_PAGE)
    page = request.GET.get('page')
    events = paginator.get_page(page)
    manager = check_if_manager(request.user)

    if request.method == 'POST':
        if 'dont_recommend' in request.POST:
            event_pk = request.POST['event_pk']
            try:
                request.user.profile.dont_recommend_events.remove(Event.objects.get(pk=event_pk))
            except:
                pass
            request.user.profile.save()
            messages.add_message(request,messages.constants.SUCCESS,f"The event {Event.objects.get(pk=event_pk).title} will be recommended to you again in event feed.")
        return redirect("dont-recommend-events", pk=request.user.pk)

    return render(request, 'events/dont_recommend_events.html', {'events': events, 'PAGE_PER_PAGE':PAGE_PER_PAGE,'events_attending': events_attending, "manager":manager, 'exclude':['fee','location','description','time']})


COMMENT_PER_PAGE = 10
@login_required
def event_detail(request, pk):
    can_change = False
    event = Event.objects.get(pk=pk)
    is_liked = len(EventHeart.objects.filter(event=event, user=request.user))==0
    images = event.event_images.all()
    all_attendants_list = event.users.all()
    is_attending = event.users.filter(id=request.user.id).exists()
    comments = event.comments_event.all().order_by('-created_time')
    paginator = Paginator(comments, COMMENT_PER_PAGE)
    page = request.GET.get('page')
    comments = paginator.get_page(page)
    try:
        if request.GET["clear_notification"]=="true":
            request.user.profile.new_notification_count = 0
            request.user.save()
    except:
        pass

    # This if statement is checking if the user is capable of editing the current event. To be able to edit,
    # user has to be either from the staff or the manager of the club that posted the event.
    if request.user in event.social_club.managers.all() or request.user.is_staff: 
        can_change = True
    if request.method == 'POST':
        if 'attend' in request.POST:
            event.users.add(request.user)
            messages.add_message(request,messages.constants.SUCCESS,f'You have successfully attended to the event')
            request.user.notifications.create(title=f'You have attended to the event {event.title}', description="Check out the event!", url=reverse("event-detail", args=[event.pk]), event=event)

        elif 'unattend' in request.POST:
            event.users.remove(request.user)
            messages.add_message(request, messages.constants.SUCCESS, f'You have successfully unattended to the event')
            request.user.notifications.create(title=f'You have unattended to the event {event.title}', description="Check out the event if you changed your mind!", url=reverse("event-detail", args=[event.pk]), event=event)
        
        elif 'edit_comment' in request.POST:
            comment = event.comments_event.get(pk=request.POST['comment_pk'])
            if comment.commentor.pk == request.user or can_change:
                comment.comment = request.POST['edit_comment']
                comment.save()
                request.user.notifications.create(title=f'Edited Comment On The Event {event.title}', description="You have edited your comment on the event", event=event, url=reverse("event-detail", args=[event.pk]))
                messages.add_message(request, messages.constants.SUCCESS, f'You have successfully edited the comment.')
            else:
                raise PermissionDenied
            
        elif 'edit_reply' in request.POST:
            comment = event.comments_event.get(pk=request.POST['comment_pk'])
            if comment.commentor.pk == request.user or can_change:
                comment.comment = request.POST['edit_reply']
                comment.save()
                request.user.notifications.create(title=f'Edited Reply On The Event {event.title}', description="You have edited your comment on the event", event=event, url=reverse("event-detail", args=[event.pk]))
                messages.add_message(request, messages.constants.SUCCESS, f'You have successfully edited the reply.')
            else:
                raise PermissionDenied
            

        elif 'delete' in request.POST:
            comment = event.comments_event.filter(pk=request.POST['comment_pk'])
            request.user.notifications.create(title=f'Deleted Comment On The Event {event.title}', description="You have deleted your comment on the event", event=event, url=reverse("event-detail", args=[event.pk]))
            messages.add_message(request, messages.constants.SUCCESS, f'You have successfully deleted the comment')
            comment.delete()

        elif 'delete_reply' in request.POST:
            comment = event.comments_event.filter(pk=request.POST['comment_pk'])
            request.user.notifications.create(title=f'Deleted Comment On The Event {event.title}', description="You have deleted your reply", event=event, url=reverse("event-detail", args=[event.pk]))
            messages.add_message(request, messages.constants.SUCCESS, f'You have successfully deleted the reply.')
            comment.delete()


            

        elif 'like' in request.POST:
            likes = event.likes_event
            if len(EventHeart.objects.filter(event=event, user=request.user))==0:
                likes.create(event=event, user=request.user)
            else:
                EventHeart.objects.filter(event=event, user=request.user).delete()

        elif 'comment' in request.POST:
            comment = request.POST['comment']
            event.comments_event.create(comment=comment, commentor=request.user)
            request.user.notifications.create(title=f'You have commented on the event {event.title}', description="Go check your comment!", url=reverse("event-detail", args=[event.pk]),event=event)
            messages.add_message(request, messages.constants.SUCCESS, f'You have successfully commented!')

        elif 'reply' in request.POST:
            reply = request.POST['reply']
            reply_to = event.comments_event.get(pk=request.POST['reply_to'])
            event.comments_event.create(reply_to=reply_to,comment=reply, commentor=request.user)
            request.user.notifications.create(title=f'You have replied a comment on the event {event.title}', description="Go check your comment!", url=reverse("event-detail", args=[event.pk]),event=event)
            if not request.user == reply_to.commentor:
                reply_to.commentor.notifications.create(title=f'{request.user} to replied your comment! {event.title}', description="Go check your comment!", url=reverse("event-detail", args=[event.pk]),event=event)
            messages.add_message(request, messages.constants.SUCCESS, f'You have successfully commented!')

        return redirect("event-detail", pk=pk)
    context={
            'event': event,
            'is_attending': is_attending,
            "shortened_attendant_list":all_attendants_list, 
            'can_change':can_change,
            'images':images,'comments':comments,
            "is_liked":is_liked, 
            'PAGE_PER_PAGE':PAGE_PER_PAGE
            }
    return render(request, 'events/event_detail.html', context=context)

@login_required
def create_event(request):
    # If the current user is not a manager at any social club, raise a permission error.
    if not check_if_manager(request.user):
        raise PermissionDenied()
    
    if request.method == 'POST':
        form = CreateEventForm(request.POST, user=request.user)
        image_form = EventImageForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()

            # Get the list of image IDs to keep
            add_images = request.POST.getlist('keep_image_add')
    
            # Save new images
            for image in request.FILES.getlist('images'):
                if str(image) in add_images: 
                    EventImage.objects.create(event=event, image=image)

            event.users.add(request.user)
            
            return redirect('event-detail', pk=event.pk)
    else:
        form = CreateEventForm(user=request.user)
        image_form = EventImageForm()
    return render(request, 'events/create_event.html', {'form': form, 'image_form':image_form, "create":True})

@login_required
def edit_event(request, pk):
    # If the current user is not a manager at any social club, raise a permission error.
    if not check_if_manager(request.user):
        raise PermissionDenied()
    
    event = Event.objects.get(pk=pk)
    if request.user in event.social_club.managers.all() or request.user.is_staff: 
        if request.method == 'POST':
            
            form = CreateEventForm(request.POST,instance=event, user=request.user)
            image_form = EventImageForm(request.POST, instance=event)
            if form.is_valid():
                form.save()
                # Get the list of image IDs to keep
                add_images = request.POST.getlist('keep_image_add')
                

                # Delete the images that were unchecked
                no_delete_images = request.POST.getlist('no_delete_image')
                
                
                # Look for all of the images' id's, delete the ones that do not appear in no_delete_images.
                to_delete = [x.id for x in event.event_images.all()]
                
                
                for image_id in to_delete:
                    if str(image_id) not in no_delete_images:
            
                        image = event.event_images.get(id=image_id)
                        image.delete()
                    



                # Save new images

                for image in request.FILES.getlist('images'):
                    
                    if str(image) in add_images: 
                        
                        EventImage.objects.create(event=event, image=image)

                return redirect('event-detail', pk=event.pk)


        else:
            form = CreateEventForm(instance=event, user=request.user)
            image_form = EventImageForm(instance=event)

        return render(request, 'events/edit_event.html', {'form':form, 'image_form':image_form})


@login_required
def delete_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if not request.user in event.social_club.managers.all() or not request.user.is_staff: 
        raise PermissionDenied()
    else:

        event.delete()
        messages.add_message(request, messages.constants.ERROR, "Event deleted!")
        return redirect('events')

@login_required
def delete_comment(request,pk):
    
    comment = get_object_or_404(EventComment, pk=pk)
    is_reply = comment.reply_to
    comment_event = comment.event
    if request.user == comment.commentor:
        comment.delete()
    else:
        raise PermissionDenied
    if is_reply:
        print('wtf')
    messages.add_message(request, messages.constants.SUCCESS, f"Your {'reply' if is_reply else 'reply'} is deleted!")
    return redirect('event-detail', pk=comment_event.pk)



@login_required
def toggle_recommend_event(request,pk,detail='false'):
    if get_object_or_404(Event, pk=pk) in request.user.profile.dont_recommend_events.all():
        request.user.profile.dont_recommend_events.remove(Event.objects.get(pk=pk))
        messages.add_message(request,messages.constants.SUCCESS,f"The event {Event.objects.get(pk=pk).title} will be recommended to you again.")
    else:
        request.user.profile.dont_recommend_events.add(Event.objects.get(pk=pk))
        messages.add_message(request,messages.constants.SUCCESS,f"The event {Event.objects.get(pk=pk).title} won't be recommended to you again.")
    request.user.profile.save()
    if detail=='true':
        return redirect('event-detail',pk=pk)
    else:
        return redirect('events')  

@login_required
def toggle_like_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    likes = event.likes_event
    if len(EventHeart.objects.filter(event=event, user=request.user))==0:
        likes.create(event=event, user=request.user)
        messages.add_message(request, messages.constants.SUCCESS, f'You have liked the event {event.title}!')
    else:
        EventHeart.objects.filter(event=event, user=request.user).all().delete()
        messages.add_message(request, messages.constants.SUCCESS, f'You have un-liked the event {event.title}!')
    return redirect('events')


@login_required
def my_events(request):
    events = Event.objects.filter(users=request.user).order_by('-created_time')
    paginator = Paginator(events, EVENT_PER_PAGE)
    page = request.GET.get('page')
    events = paginator.get_page(page)
    return render(request, 'events/my_events.html', {'events': events, 'PAGE_PER_PAGE':PAGE_PER_PAGE, 'exclude':['fee','location','description','time']})


@login_required
def search(request):
    try:
        query = request.GET.get('q').split('&')[0]
    except AttributeError:
        query = request.GET.get('q')


    events = Event.objects.filter(Q(title__icontains=query) | Q(social_club__name__icontains=query)).annotate(is_attending=Count('users', filter=Q(users=request.user))) \
        .annotate(is_liked=Count('likes_event', filter=Q(likes_event__user=request.user))) \
        .order_by('-is_liked', '-is_attending', '-created_time')

    paginator = Paginator(events, EVENT_PER_PAGE)
    page = request.GET.get('page')
    events = paginator.get_page(page)
    return render(request, 'events/my_events.html', {'events': events, 'PAGE_PER_PAGE':PAGE_PER_PAGE, 'exclude':['fee','location','description','time']})