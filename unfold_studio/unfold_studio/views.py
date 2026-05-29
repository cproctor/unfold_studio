from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings as s
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Q, F
from django.db import OperationalError, transaction
from django.core.paginator import Paginator
import structlog

from stories.models import Story
from profiles.forms import SignUpForm, StudentSignUpForm
from unfold_studio.forms import SearchForm
from literacy_groups.models import JoinCode
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

log = structlog.get_logger("unfold_studio")


def u(request):
    "Helper to return username"
    return request.user.username if request.user.is_authenticated else "<anonymous>"


def home(request):
    "The homepage shows a subset of stories with the highest priority."
    if request.user.is_authenticated:
        for g in request.user.groups.filter(id__in=s.GROUP_HOMEPAGE_MESSAGES.keys()).all():
            messages.warning(request, s.GROUP_HOMEPAGE_MESSAGES[g.id])
        stories = Story.objects.for_user(request.user)
        stories = stories.select_related('author').prefetch_related('loves')
    else:
        stories = Story.objects.for_anonymous_user()

    stories = stories[:s.STORIES_ON_HOMEPAGE]
    return render(request, 'unfold_studio/home.html', {'stories': stories})


def browse(request):
    "Shows all stories, sorted by priority."
    if request.user.is_authenticated:
        stories = Story.objects.for_user(request.user)
    else:
        stories = Story.objects.for_anonymous_user()

    if request.GET.get('query'):
        form = SearchForm(request.GET)
        if form.is_valid():
            query = SearchQuery(form.cleaned_data['query'])
            stories = stories.annotate(
                rank=SearchRank(F('search'), query),
                score=F('rank') * F('priority') / (F('rank') + F('priority'))
            ).filter(Q(rank__gte=s.SEARCH_RANK_CUTOFF) | Q(author__username__icontains=form.cleaned_data['query'])).order_by('-score')
        else:
            messages.warning(request, "Please enter a valid search query")
            return redirect('list_stories')
    else:
        form = SearchForm()

    if request.user.is_authenticated:
        stories = stories.select_related('author').prefetch_related('loves')

    paginator = Paginator(stories, s.STORIES_PER_PAGE)
    page = request.GET.get('page', 1)
    try:
        story_page = paginator.page(page)
        return render(request, 'unfold_studio/list_stories.html', {
            'stories': story_page,
            'form': form
        })
    except OperationalError:
        messages.warning(request, "Search is not supported using the current database.")
        return redirect('list_stories')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request,
                "Welcome to Unfold Studio! Have fun, and please be a good community member.")
            log.info(name="Application Alert", event="New User Sign Up", arg={"user": u(request)})
            return redirect('home')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})


def join_student(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    code_str = request.POST.get('join_code')
                    try:
                        join_code = JoinCode.objects.get(code=code_str, assigned_user__isnull=True)
                        user.literacy_groups.add(join_code.group)
                        join_code.assigned_user = user
                        join_code.save()
                        log.info(event="Student Sign Up Successful", arg={"user": user.username})
                        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                        return redirect('home')
                    except JoinCode.DoesNotExist:
                        raise ValueError("Invalid or expired join code.")
            except ValueError as e:
                messages.error(request, str(e))
                return render(request, 'registration/join_student.html', {'form': form})
    else:
        form = StudentSignUpForm()
    return render(request, 'registration/join_student.html', {'form': form})

