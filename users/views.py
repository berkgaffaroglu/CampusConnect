from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.contrib import messages
from django.db.models import Q
from django.contrib.messages.views import SuccessMessageMixin
from django.views import View
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from events.models import Event
from social_clubs.models import SocialClub
from urllib.parse import urlencode



from .forms import RegisterForm, LoginForm, UpdateUserForm, UpdateProfileForm
from .models import User
@login_required
def home(request):
    return render(request, 'users/home.html')




class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'users/register.html'

    def dispatch(self, request, *args, **kwargs):
        # will redirect to the home page if a user tries to access the register page while logged in
        if request.user.is_authenticated:
            return redirect(to='/')

        # else process dispatch as it otherwise normally would
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')

            return redirect(to='login')

        return render(request, self.template_name, {'form': form})


# Class based view that extends from the built in login view to add a remember me functionality
class CustomLoginView(LoginView):
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
            # set session expiry to 0 seconds. So it will automatically close the session after the browser is closed.
            self.request.session.set_expiry(0)

            # Set session as modified to force data updates/cookie to be saved.
            self.request.session.modified = True
        else:
            self.request.session.set_expiry(1209600)
        # else browser session will be as long as the session cookie time "SESSION_COOKIE_AGE" defined in settings.py
        return super(CustomLoginView, self).form_valid(form)


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('users-home')


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'users/change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('users-home')


EVENT_PER_PAGE = 10
PAGE_PER_PAGE = 5
@login_required
def profile(request, pk):
    is_manager_of_query_club = False
    current_profile = get_object_or_404(User, pk=pk)
    if request.method == 'GET':
        if request.user.is_authenticated:
            if request.user.pk == pk:
                can_change = True
            else:
                can_change = False
        created_events = current_profile.created_events.all()
        clubs = current_profile.clubs_joined.all()
        if request.GET.get('club'):
            query_club = get_object_or_404(SocialClub, pk=request.GET.get('club'))
            if current_profile in query_club.managers.all():
                is_manager_of_query_club = True
            else:
                False
        else:
            query_club = None
        events = Event.objects.filter(users=current_profile).order_by('-created_time')
        events_attending = Event.objects.filter(users=request.user)
        paginator = Paginator(events, EVENT_PER_PAGE)
        page = request.GET.get('page')
        events = paginator.get_page(page)

     

        context = {'events': events, 
                   'PAGE_PER_PAGE':PAGE_PER_PAGE,
                    'events_attending': events_attending,
                    'can_change': can_change, 
                    'current_profile':current_profile, 
                    'created_events':created_events,
                    'clubs':clubs,
                    'exclude':['time','fee','location','description'],
                    'query_club':query_club,
                    'is_manager_of_query_club':is_manager_of_query_club
                    }
        

        return render(request, 'users/profile.html', context)
    
    elif request.method == 'POST':

        if 'auth' in request.POST:
            setattr(current_profile.profile,'ambassador', True)
            current_profile.save()
            messages.add_message(request,messages.constants.SUCCESS,f'You have successfully assigned {current_profile.username} as an ambassador!')
            request.user.notifications.create(title=f'You have successfully assigned {current_profile.username} as an ambassador!', description="Go to the profile if you change your mind!", url=reverse("users-profile", args=[current_profile.pk]))
            current_profile.notifications.create(title=f'You are now an ambassador!', description="Now you can create social clubs!")
            URL = reverse('users-profile', kwargs={'pk': pk})
            if request.POST["club_pk"]:
                URL += f'?club={request.POST["club_pk"]}'
            return redirect(URL)

        elif 'unauth' in request.POST:
            setattr(current_profile.profile,'ambassador', False)
            current_profile.save()
            messages.add_message(request, messages.constants.SUCCESS, f'You have successfully un-assigned {current_profile.username} as an ambassador!')
            request.user.notifications.create(title=f'You have successfully un-assigned {current_profile.username} as an ambassador!', description="Go to the profile if you change your mind!", url=reverse("users-profile", args=[current_profile.pk]))
            current_profile.notifications.create(title=f'You are not an ambassador anymore!', description="Now you can't create social clubs!")
            URL = reverse('users-profile', kwargs={'pk': pk})
            if request.POST["club_pk"]:
                URL += f'?club={request.POST["club_pk"]}'
            return redirect(URL)
        
        elif 'assign' in request.POST:

            query_club = SocialClub.objects.get(pk=request.POST['club_pk'])
            query_club.managers.add(current_profile)
            query_club.save()

            messages.add_message(request, messages.constants.SUCCESS, f'You have successfully assigned {current_profile.username} as a manager!')
            request.user.notifications.create(title=f'You have successfully assigned {current_profile.username} as a manager', description=f"{current_profile.username} now manages the club {query_club.name}", url=reverse('club-detail', args=[query_club.pk]))
            current_profile.notifications.create(title=f'Now you are the manager of the club {query_club.name}', description=f"{request.user} assigned you to manage {query_club.name}", url=reverse('club-detail', args=[query_club.pk]))
            URL = reverse('users-profile', kwargs={'pk': pk})
            URL += f'?club={request.POST["club_pk"]}'
            return redirect(URL)
        
        elif 'unassign' in request.POST:
            
            query_club = SocialClub.objects.get(pk=request.POST['club_pk'])
            query_club.managers.remove(current_profile)
            query_club.save()
            messages.add_message(request, messages.constants.SUCCESS, f'You have successfully un-assigned {current_profile.username} as a manager!')
            request.user.notifications.create(title=f'You have successfully un-assigned {current_profile.username} as a manager', description=f"{current_profile.username} now doesn't manage the club {query_club.name}", url=reverse('club-detail', args=[query_club.pk]))
            current_profile.notifications.create(title=f'Now you are the manager of the club {query_club.name}', description=f"{request.user} assigned you to manage {query_club.name}", url=reverse('club-detail', args=[query_club.pk]))
            URL = reverse('users-profile', kwargs={'pk': pk})
            URL += f'?club={request.POST["club_pk"]}'
            return redirect(URL)
        
        elif 'ban' in request.POST:
            current_profile.is_active = False
            current_profile.save()
            messages.add_message(request, messages.constants.SUCCESS, f'You have successfully banned {current_profile.username}')
            request.user.notifications.create(title=f'You have successfully banned the user {current_profile.username}', description=f"{current_profile.username} is now banned", url=reverse('users-profile', args=[current_profile.pk]))
            current_profile.notifications.create(title=f'{request.user} has banned you.', description=f"You can no longer access the platform.")
            URL = reverse('users-profile', kwargs={'pk': current_profile.pk})
            if request.POST["club_pk"]:
                URL += f'?club={request.POST["club_pk"]}'
            return redirect(URL)

        elif 'unban' in request.POST:
            current_profile.is_active = True
            current_profile.save()
            messages.add_message(request, messages.constants.SUCCESS, f'You have successfully un-banned {current_profile.username}')
            request.user.notifications.create(title=f'You have successfully un-banned the user {current_profile.username}', description=f"{current_profile.username} can now access the platform.", url=reverse('users-profile', args=[current_profile.pk]))
            current_profile.notifications.create(title=f'{request.user} has un-banned you.', description=f"You can now access the platform.")
            URL = reverse('users-profile', kwargs={'pk': current_profile.pk})
            if request.POST["club_pk"]:
                URL += f'?club={request.POST["club_pk"]}'
            return redirect(URL)
        
        elif request.method == "POST":
            if "clear" in request.POST:
                current_profile.profile.dont_recommend_events.clear()
                current_profile.profile.save()
                messages.add_message(request, messages.constants.SUCCESS, "You have successfully cleared your 'Dont Recommend List'")
                URL = reverse('users-profile', kwargs={'pk': current_profile.pk})
                if request.POST["club_pk"]:
                    URL += f'?club={request.POST["club_pk"]}'
                return redirect(URL)


        

@login_required
def edit_profile(request,pk):
    if request.user.pk == pk:
            if request.method == 'POST':
                user_form = UpdateUserForm(request.POST, instance=request.user)
                profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)
            
                if user_form.is_valid() and profile_form.is_valid():
                    user_form.save()
                    profile_form.save()
                    messages.success(request, 'Your profile is updated successfully')
                    return redirect(to='users-profile',pk=pk)
            else:
                user_form = UpdateUserForm(instance=request.user)
                profile_form = UpdateProfileForm(instance=request.user.profile)

            return render(request, 'users/edit_profile.html', {'user_form': user_form, 'profile_form': profile_form, 'can_change': True})
    else:
        raise PermissionDenied("You can't edit this profile!")
    
USER_PER_PAGE = 50
@staff_member_required
def users(request):
    query = request.GET.get('q')
    if query:
        users = User.objects.filter(Q(username__icontains=query) | Q(first_name__icontains=query))
    else:
        users = User.objects.all().order_by('-is_staff', '-profile__ambassador', 'username')
        
    paginator = Paginator(users, USER_PER_PAGE)
    page = request.GET.get('page')
    users = paginator.get_page(page)
    return render(request, 'users/users.html', {'users':users,"query":query,'PAGE_PER_PAGE':PAGE_PER_PAGE})


NOTIFICATON_PER_PAGE = 10
@login_required
def notification(request):
    notifications = request.user.notifications.all().order_by('-created_time')
    if request.method == 'POST':
        if 'clear' in request.POST:
            notifications.delete()
    
    new_notification_count = request.user.profile.new_notification_count
    request.user.profile.new_notification_count = 0
    request.user.save()
    paginator = Paginator(notifications, NOTIFICATON_PER_PAGE)
    page = request.GET.get('page')
    notifications = paginator.get_page(page)
    return render(request, 'users/notifications.html', {'notifications':notifications,'PAGE_PER_PAGE':PAGE_PER_PAGE, 'new_notification_count':new_notification_count})
