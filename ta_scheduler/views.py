from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

from ta_app.forms import UserForm, PublicProfileForm, PrivateProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from ta_app.forms import CourseAdminForm
from .models import Section, Course, DAYS_OF_WEEK, PublicProfile, PrivateProfile, CourseInstructor, SectionTA
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
from django.core.mail import send_mail


from ta_app.forms import CourseForm
from ta_scheduler.models import Course

User = get_user_model()
temp_email = {}  #temp stores email for reset



def HomePageTemplate(request):
    return render(request, 'HomePageTemplate.html')


def courseDeletion(course_id):
    Course.objects.filter(id=course_id).delete()

def courseCreation(request):
    course_name = request.POST.get('course_name')
    semester_choice = request.POST.get('semester')
    course_year = request.POST.get('year')


    Course.objects.create(
        courseName=course_name,
        semester=semester_choice,
        year=course_year,
    )


@login_required
def courses(request):
    user = request.user
    if request.method == 'POST':
        #if the request post is delete it will do this
        if 'delete_course_id' in request.POST:
            course_id = request.POST.get('delete_course_id')
            courseDeletion(course_id)
        #if the request post is to add it will do this
        else:
            courseCreation(request)


        return redirect('courses')

    #allcourses = Course.objects.all() we only want to view all courses if we are an admin
    allcourses = []
    sections = []
    #sections = Section.objects.all() we only want to view all sections if we are an admin and limit it for other users
    if(user.role == 'instructor'):
       # sections = [Section.objects.get(instructor=user)]
        allcourses = [ci.course for ci in CourseInstructor.objects.filter(instructor = user)]
    if(user.role == 'admin'):
        sections = Section.objects.all()
        allcourses = Course.objects.all()

    if(user.role == 'ta'):
        sections = [st.section for st in SectionTA.objects.filter(ta = user)]
        allcourses = [sc.course for sc in sections]
    if(user.role == 'admin'):
        sections = Section.objects.all()
        allcourses = Course.objects.all()
    users = User.objects.filter(role__in=['ta', 'instructor'])

    return render(request, 'Courses.html', {
        'sections': sections,
        'courses': allcourses,
        'SEMESTER_CHOICES': Course.SEMESTER_CHOICES,
        'users': users,


    })





@login_required
def home(request):
    return render(request, 'Home.html')


def loginUser(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'Login.html', {'error': 'Invalid username or password'})
    else:
        return render(request, 'Login.html', {'error': None})

def redirectToCourse():
    return redirect('courses')

def getSectionName(request):
    return request.POST.get('section_name')

def getSectionDay(request):
    return request.POST.get('day1')

def getSectionDayTwo(request):
    return request.POST.get('day2')

def getSectionStartTime(request):
    return request.POST.get('start_time')

def getSectionEndTime(request):
    return request.POST.get('end_time')

def getSectionTeacher(request):
    return request.POST.get('teacher')



def sectionCreation(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id)
        section_name = getSectionName(request)
        day_of_week = getSectionDay(request)
        day_of_week_optional = getSectionDayTwo(request)
        start_time = getSectionStartTime(request)
        end_time = getSectionEndTime(request)
        teacher_id = getSectionTeacher(request)

        teacher = User.objects.filter(id=teacher_id).first()

        if teacher.role == 'instructor':
            instructor = teacher
            CourseInstructor.objects.create(instructor = teacher, course = course)
            ta = None
        elif teacher.role == 'ta':
            instructor = None
            ta = teacher
        else:
            instructor = None
            ta = None

        Section.objects.create(
            course=course,
            sectionName=section_name,
            dayOfWeek=day_of_week,
            dayOfWeek2 = day_of_week_optional,
            timeOfDay=start_time,
            endOfDay=end_time,
            instructor=instructor,
            teaching_assistant=ta,

        )
        if(teacher.role =='ta'):
            p = Section.objects.get(sectionName = section_name, course = course, dayOfWeek=day_of_week, dayOfWeek2 = day_of_week_optional, timeOfDay=start_time, endOfDay = end_time, instructor = instructor, teaching_assistant=ta)
            SectionTA.objects.create(ta = teacher, section = p)
    return redirect('course_detail', course_id=course_id)


def sectionDeletion(section_id):
    Section.objects.filter(id=section_id).delete()


def sectionEdit(request, section_id):

    section = get_object_or_404(Section, id=section_id)

    section.sectionName = getSectionName(request)
    section.dayOfWeek = getSectionDay(request)
    section.dayOfWeek2 = getSectionDayTwo(request)
    section.timeOfDay = getSectionStartTime(request)
    section.endOfDay = getSectionEndTime(request)

    teacher_id = getSectionTeacher(request)

    teacher = User.objects.filter(id=teacher_id).first()

    if teacher.role == 'instructor':
        section.instructor = teacher
        section.teaching_assistant = None
    elif teacher.role == 'ta':
        section.teaching_assistant = teacher
        section.instructor = None
    else:
        section.instructor = None
        section.ta = None





    section.save()
    return redirect('course_detail', course_id=section.course.id)






@login_required()
def course_detail(request, course_id):
    # either you find the course or you dont
    user = request.user
    course = get_object_or_404(Course, id=course_id)
    users = User.objects.filter(role__in=['ta', 'instructor'])
    if request.method == 'POST':
        if 'back-button' in request.POST:
            return redirectToCourse()
        if 'delete_section' in request.POST:
            section_id = request.POST.get('delete_section')
            sectionDeletion(section_id)
            return redirect('course_detail', course_id=course_id)
        if 'edit_section' in request.POST:
            section_id = request.POST.get('edit_section_id')
            if section_id:
                sectionEdit(request, section_id)
                return redirect('course_detail', course_id=course_id)

        else:
            return sectionCreation(request, course_id)
    if(user.role == 'ta'):
        sections = Section.objects.filter(course=course, teaching_assistant=user)
    elif(user.role == 'instructor'):

        sections = Section.objects.filter(course = course)
    else:
        sections = Section.objects.filter(course=course)
    # Renders the html for the course that is clicked
    return render(request, 'course_detail.html', {
        'course': course,
        'users': users,
        'DAYS_OF_WEEK': DAYS_OF_WEEK,
        'sections': sections,


    })



User = get_user_model()

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == 'admin'                    #admin only restriction


class OwnerOrAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return self.request.user == obj or self.request.user.role == 'admin'            #logged in user and admin only restriction


class UserListView(ListView):
    model = User
    template_name = 'user_list.html'
    context_object_name = 'users'
    ordering = ['full_name']

class UserCreateView(AdminRequiredMixin, CreateView):
    model = User
    form_class = UserForm
    template_name = 'user_form.html'
    success_url = reverse_lazy('user-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'profile_form' not in context:
            context['profile_form'] = PublicProfileForm()
            context.setdefault('private_profile_form', PrivateProfileForm())
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        profile_form = PublicProfileForm(self.request.POST)
        private_profile_form = PrivateProfileForm(self.request.POST)
        if form.is_valid() and profile_form.is_valid() and private_profile_form.is_valid():
            user = form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            private_profile = private_profile_form.save(commit=False)
            private_profile.user = user
            private_profile.save()

            return redirect(self.success_url)
        return self.render_to_response(self.get_context_data(form=form, profile_form=profile_form, private_profile_form=private_profile_form))

class UserUpdateView(OwnerOrAdminRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'user_form.html'
    success_url = reverse_lazy('user-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()                  #passes request.user into the form
        kwargs['request_user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        profile = user.public_profile.first()  # <--- get the PublicProfile instance here
        if 'profile_form' not in context:
            context['profile_form'] = PublicProfileForm(instance=profile)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        profile_instance = self.object.public_profile.first()
        profile_form = PublicProfileForm(request.POST, instance=profile_instance)

        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            profile = profile_form.save(commit=False)
            profile.user = user   # Make sure to link profile to user
            profile.save()
            return redirect(self.success_url)

        return self.render_to_response(self.get_context_data(form=form, profile_form=profile_form))
class UserDetailView(DetailView):
    model = User
    template_name = 'view_profile.html'
    context_object_name = 'user'
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['delete_mode'] = self.request.path.endswith('confirm_delete/')
        ctx['public_profile'] = self.object.public_profile.first()
        return ctx


def user_delete(request, pk):
    if request.method == 'POST' and request.user.role == 'admin':
        get_object_or_404(User, pk=pk).delete()
    return redirect('user-list')

User = get_user_model()

class PublicProfileView(DetailView):
    model = PublicProfile
    template_name = 'user_form.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        return get_object_or_404(PublicProfile, user=user)



#most likely wrong idk, cant find urls when testing
class PrivateProfileView(DetailView):
    model = PrivateProfile
    template_name = 'user_form.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        profile = get_object_or_404(PrivateProfile, user=user)

        request_user = self.request.user
        if not request_user.is_authenticated:
            raise PermissionDenied("You must be logged in to view this private profile.")

        # Only the owner or a user with the 'admin' role can access this
        if self.request.user != user and self.request.user.role != 'admin':
            raise PermissionDenied("You do not have permission to view this private profile.")
        return profile

User = get_user_model()

class EditPublicProfileView(UpdateView):
    model = PublicProfile
    fields = ['bio']
    template_name = 'edit_public_profile.html'

    def get_object(self, queryset=None):
        # return the profile of the currently logged-in user
        return PublicProfile.objects.get(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_object()  # So the template gets `profile.user.username`
        return context

    def get_success_url(self):
        # Redirect to the public profile page after saving
        return reverse('public_profile', kwargs={'username': self.request.user.username})


class PrivateProfileUpdateView(OwnerOrAdminRequiredMixin, UpdateView):
    model = PrivateProfile
    form_class = PrivateProfileForm
    template_name = 'Private_profile_form.html'
    success_url = reverse_lazy('user_list')

    def get_object(self, queryset=None):
        return PrivateProfile.objects.get(user=self.request.user)

@csrf_exempt
def reset_password(request):
    context = {}

    if request.method == "POST":
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        try:
            user = User.objects.get(email=email)

            if password1 != password2:
                context["error"] = "Passwords do not match."
            else:
                user.set_password(password1)
                user.save()
                return redirect("login")
        except User.DoesNotExist:
            context["error"] = "No account associated with this email."

    return render(request, "reset_password.html", context)

