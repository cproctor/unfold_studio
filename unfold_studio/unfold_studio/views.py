from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.conf import settings as s
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, F, Value, FloatField
from django.db.models.functions import Coalesce
from django.db import OperationalError, transaction
from django.core.paginator import Paginator
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
import structlog

from stories.models import Story
from stories.genres import get_top_genres, genre_label
from comments.models import Comment
from profiles.forms import SignUpForm, StudentSignUpForm
from unfold_studio.forms import SearchForm
from unfold_studio.anonymous_session import get_anonymous_owned_story_ids, remove_anonymous_owned_story
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
        base_stories = Story.objects.for_user(request.user)
    else:
        base_stories = Story.objects.for_anonymous_user()

    # Genre filter
    current_genre = request.GET.get('genre', '')
    if current_genre:
        stories = base_stories.filter(genres__contains=[current_genre])
    else:
        stories = base_stories

    # Build sidebar genre links from top tags across all visible stories
    top_genres = get_top_genres(base_stories, s.GENRE_BROWSE_TAG_COUNT)
    genre_links = [{'slug': '', 'label': 'All', 'qs': ''}] + [
        {'slug': g, 'label': genre_label(g), 'qs': f'genre={g}'}
        for g in top_genres
    ]

    raw_q = ''
    if request.GET.get('query'):
        form = SearchForm(request.GET)
        if form.is_valid():
            raw_q = (form.cleaned_data.get('query') or '').strip()
            if not raw_q:
                messages.warning(request, "Please enter a valid search query")
                return redirect('list_stories')

            # websearch: friendlier multi-word matching than plainto_tsquery.
            query = SearchQuery(raw_q, search_type='websearch')

            # Substring fallback: FTS misses many title/ink cases; also match each word (len>=3).
            text_q = Q(title__icontains=raw_q) | Q(ink__icontains=raw_q)
            for w in raw_q.split():
                w = w.strip('.,!?\"\'()[]')
                if len(w) >= 3:
                    text_q |= Q(title__icontains=w) | Q(ink__icontains=w)

            stories = stories.annotate(
                rank=SearchRank(F('search'), query),
                score=Coalesce(
                    F('rank') * F('priority') / (F('rank') + F('priority')),
                    Value(0.0),
                    output_field=FloatField(),
                ),
            ).filter(
                Q(rank__gte=s.SEARCH_RANK_CUTOFF)
                | Q(author__username__icontains=raw_q)
                | text_q
            ).exclude(
                author__isnull=True, public=False, shared=False
            ).order_by('-score', '-priority')
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
        qs_parts = []
        if current_genre:
            qs_parts.append(f'genre={current_genre}')
        if raw_q:
            qs_parts.append(f'query={raw_q}')
        return render(request, 'unfold_studio/list_stories.html', {
            'stories': story_page,
            'form': form,
            'genre_links': genre_links,
            'current_genre': current_genre,
            'search_value': raw_q,
            'has_search_query': form.is_bound,
            'browse_querystring': '&'.join(qs_parts),
        })
    except OperationalError:
        messages.warning(request, "Search is not supported using the current database.")
        return redirect('list_stories')


class ClaimAwareLoginView(LoginView):
    """
    After username/password login, attach an anonymous session-owned story to the user
    when claim_story is present (same rules as signup).
    """

    template_name = "registration/login.html"

    def get(self, request, *args, **kwargs):
        raw = request.GET.get("claim_story")
        if raw is not None and str(raw).strip().isdigit():
            request.session["pending_claim_story"] = int(str(raw).strip())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        raw = self.request.GET.get("claim_story")
        if raw is not None and str(raw).strip().isdigit():
            ctx["claim_story_id"] = int(str(raw).strip())
        return ctx

    def form_valid(self, form):
        response = super().form_valid(form)
        claim_id = None
        raw = self.request.POST.get("claim_story")
        if raw is not None and str(raw).strip().isdigit():
            claim_id = int(str(raw).strip())
        if claim_id is None:
            claim_id = self.request.session.pop("pending_claim_story", None)
        if claim_id is None:
            return response
        if claim_id not in get_anonymous_owned_story_ids(self.request):
            return response
        story = Story.objects.filter(pk=claim_id, author__isnull=True).first()
        if not story:
            return response
        story.author = self.request.user
        story.save()
        remove_anonymous_owned_story(self.request, claim_id)
        return redirect("show_story", claim_id)


def signup(request):
    claim_story_raw = request.POST.get('claim_story') if request.method == 'POST' else request.GET.get('claim_story')
    claim_story_id = None
    if claim_story_raw is not None and str(claim_story_raw).strip().isdigit():
        claim_story_id = int(str(claim_story_raw).strip())

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    role = form.cleaned_data.get('user_type')

                    if role == 'student':
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

                    elif role == 'teacher':
                        messages.info(request,
                            "Account created! To request instructor access, please contact us "
                            "with your username, name, institution, and how you plan to use Unfold Studio. "
                            "Until then, your account is a regular user.")
                        log.info(event="Teacher Sign Up (Pending)", arg={"user": user.username})
                        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                        return redirect('home')

                    else:
                        log.info(event="New User Sign Up", arg={"user": user.username})
                        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                        return redirect('home')

            except ValueError as e:
                messages.error(request, str(e))
                return render(request, 'registration/signup.html', {'form': form})
    else:
        form = SignUpForm()

    raw_next = request.POST.get('next') if request.method == 'POST' else request.GET.get('next')
    raw_next = raw_next or ''
    next_url = ''
    if raw_next and url_has_allowed_host_and_scheme(
        raw_next,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = raw_next

    return render(request, 'registration/signup.html', {
        'form': form,
        'claim_story_id': claim_story_id,
        'next_url': next_url,
    })


def join_student(request):
    prefill_code = request.GET.get('code', '')
    if request.user.is_authenticated:
        if request.method == 'POST':
            code_str = request.POST.get('join_code', '').strip()
            try:
                join_code = JoinCode.objects.get(code=code_str, assigned_user__isnull=True)
                if request.user.literacy_groups.filter(pk=join_code.group.pk).exists():
                    messages.warning(request, "You are already a member of that course.")
                else:
                    request.user.literacy_groups.add(join_code.group)
                    join_code.assigned_user = request.user
                    join_code.save()
                    log.info(event="Student Joined Course", arg={"user": request.user.username})
                    messages.success(request, "You have joined {}.".format(join_code.group.name))
                return redirect('home')
            except JoinCode.DoesNotExist:
                messages.error(request, "Invalid or expired join code.")
        return render(request, 'registration/join_student.html', {
            'authenticated': True,
            'prefill_code': prefill_code,
        })
    else:
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
                    return render(request, 'registration/join_student.html', {'form': form, 'prefill_code': prefill_code})
        else:
            form = StudentSignUpForm()
        return render(request, 'registration/join_student.html', {'form': form, 'prefill_code': prefill_code})


class SendFeedbackView(LoginRequiredMixin, View):
    """Teacher sends feedback or saves it as a draft on a student's story using the terminal tab"""

    def post(self, request, story_id):
        story = get_object_or_404(Story, pk=story_id)

        action = request.POST.get('action')
        message = request.POST.get('comment', '').strip()

        teacher_has_feedback_access = False
        if request.user.profile.is_teacher:
            teacher_has_feedback_access = story.prompts_submitted.filter(
                literacy_group__leaders=request.user,
                deleted=False
            ).exists()

        #only the teacher can send feedback
        if action == 'send':
            if not teacher_has_feedback_access:
                return HttpResponseForbidden("You do not have permission to send feedback on this story.")

            if message:
                Comment.objects.create(
                    author=request.user,
                    story=story,
                    message=message,
                )

            request.session.pop(f'draft_{story.id}', None)

        # draft only saved in session and not db
        elif action == 'draft':
            if not teacher_has_feedback_access:
                return HttpResponseForbidden("You do not have permission to save a draft on this story.")

            request.session[f'draft_{story.id}'] = message

        # student reply
        elif action == 'reply':
            if request.user != story.author:
                return HttpResponseForbidden("Only the story author can reply.")

            if message:
                Comment.objects.create(
                    author=request.user,
                    story=story,
                    message=message,
                )

        return redirect('show_story', story.id)
