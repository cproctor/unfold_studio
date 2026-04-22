from django.shortcuts import render, redirect                         
from django.http import HttpResponse, Http404                         
from django.conf import settings as s                                 
from django.shortcuts import render, get_object_or_404                
from django.views import generic                                      
from django.http import JsonResponse                                  
from django.contrib.auth import login
import json
import structlog
from .forms import StoryForm, StoryVersionForm
from .models import Story, Book, StoryPlayInstance, StoryPlayRecord
from profiles.models import Profile
from django.views.generic.detail import SingleObjectMixin, DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse
import reversion
from reversion.models import Version
from profiles.forms import SignUpForm, StudentSignUpForm
from django.utils.timezone import now
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Q, F, Window
from django.db.models.functions import RowNumber
from django.db import OperationalError
from django.core.paginator import Paginator, PageNotAnInteger
from unfold_studio.mixins import StoryMixin
from unfold_studio.forms import SearchForm
from literacy_events.models import LiteracyEvent
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from comments.models import Comment
from comments.forms import CommentForm
from django.utils import timezone
from django.db import transaction
from literacy_groups.models import JoinCode
from django.http import HttpResponseForbidden

log = structlog.get_logger("unfold_studio")    

def u(request):
    "Helper to return username"
    return request.user.username if request.user.is_authenticated else "<anonymous>"

def home(request):
    "The homepage shows a subset of stories with the highest priority."
    site = get_current_site(request)
    if request.user.is_authenticated:
        for g in request.user.groups.filter(id__in=s.GROUP_HOMEPAGE_MESSAGES.keys()).all():
            messages.warning(request, s.GROUP_HOMEPAGE_MESSAGES[g.id])
        stories = Story.objects.for_site_user(site, request.user)
        stories = stories.select_related('author').prefetch_related('loves')
    else:
        site = get_current_site(request)
        stories = Story.objects.for_site_anonymous_user(site)

    stories = stories[:s.STORIES_ON_HOMEPAGE]
    return render(request, 'unfold_studio/home.html', {'stories': stories})

def browse(request):
    "Shows all stories, sorted by priority. Someday, I'll need to paginate this."
    site = get_current_site(request)
    if request.user.is_authenticated:
        stories = Story.objects.for_site_user(site, request.user)
    else:
        stories = Story.objects.for_site_anonymous_user(site)

    if request.GET.get('query'):
        form = SearchForm(request.GET)
        if form.is_valid():
            query = SearchQuery(form.cleaned_data['query'])
            stories = stories.annotate(
                rank=SearchRank(F('search'), query), 
                score=F('rank') * F('priority') / (F('rank') + F('priority'))
            ).filter(Q(rank__gte=s.SEARCH_RANK_CUTOFF)|Q(author__username__icontains=form.cleaned_data['query'])).order_by('-score')
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

def new_story(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            story = Story(
                author=request.user, 
                creation_date=now(), 
                edit_date=now()
            )
        else: 
            story = Story(
                author=None, 
                creation_date=now(), 
                edit_date=now(), 
                public=True
            )
        form = StoryForm(request.POST, instance=story)
        if form.is_valid():
            story = form.save()
            story.compile()
            story.update_priority()
            story.sites.add(get_current_site(request))
            with reversion.create_revision():
                story.save()
                reversion.set_user(story.author)
                reversion.set_comment("Initial version of @story:{}".format(story.id))
            log.info(name="Application Alert", event="New Story Created", arg={"user": u(request), "story": story.id})
            return redirect('show_story', story.id)
    else:
        form = StoryForm()

    return render(request, 'unfold_studio/new_story.html', {'form': form})

def edit_story(request, story_id):
    story = Story.objects.get_editable_for_request_or_404(request, pk=story_id)
    story.edit_date = now()
    if request.method == "POST":
        form = StoryForm(request.POST, instance=story)
        if form.is_valid():
            story = form.save()
            with reversion.create_revision():
                story.save()
                reversion.set_user(story.author)
            return redirect('show_story', story.id)
    else:
        form = StoryForm(instance=story)
    return render(request, 'unfold_studio/edit_story.html', {'form': form, 'story': story})

def compile_story(request, story_id):
    "This is the route used to update story "
    story = Story.objects.get_editable_for_request_or_404(request, pk=story_id)
    story.edit_date = now()
    story.ink = request.POST['ink']
    story.compile()
    with reversion.create_revision():
        story.save()
        reversion.set_user(story.author)
        if not story.errors.exists():
            log.info(name="Application Alert", event="Story Editted", msg="OK", arg={"user": u(request), "story": story.id})
        else:
            log.warning(name="Application Alert", event="Story Editted", msg="Edit has Errors", arg={"user": u(request), "story": story.id})
    return JsonResponse(story.for_json())

def show_story(request, story_id):
    "Shows a story, using the same view regardless of whether it can be edited by the user"
    story = Story.objects.get_for_request_or_404(request, pk=story_id)
    editable = int(story.author == request.user or story.public)
    addableBooks = request.user.books.exclude(stories=story) if request.user.is_authenticated else []

    #Feedback terminal
    is_teacher = request.user.is_authenticated and request.user.profile.is_teacher
    is_story_author = request.user.is_authenticated and story.author == request.user

    teacher_has_feedback_access = False
    if is_teacher:
        teacher_has_feedback_access = story.prompts_submitted.filter(
            literacy_group__leaders=request.user,
            deleted=False
        ).exists()

    feedback_mode = teacher_has_feedback_access or is_story_author
    feedback_readonly = is_story_author and not teacher_has_feedback_access

    prompt_name = ''
    draft_feedback = ''
    latest_teacher_feedback = None
    latest_student_reply = None
    latest_feedback_thread = ''
    feedback_history_comments = []

    if feedback_mode:
        from prompts.models import PromptStory

        ps = PromptStory.objects.filter(story=story).select_related('prompt').first()
        if ps:
            prompt_name = ps.prompt.name

        if teacher_has_feedback_access:
            draft_feedback = request.session.get(f'draft_{story.id}', '')

        latest_teacher_feedback = Comment.objects.filter(
            story=story,
            author__profile__is_teacher=True,
            deleted=False
        ).order_by('-creation_date').first()

        latest_student_reply = Comment.objects.filter(
            story=story,
            author=story.author,
            deleted=False
        ).order_by('-creation_date').first()

        feedback_history_comments = Comment.objects.for_story(story).order_by('creation_date')

        if latest_teacher_feedback:
            latest_feedback_thread = "Teacher:\n{}".format(latest_teacher_feedback.message)

        if latest_student_reply:
            if latest_feedback_thread:
                latest_feedback_thread += "\n\n"
            latest_feedback_thread += "You:\n{}".format(latest_student_reply.message)

    return render(request, 'unfold_studio/show_story.html', {
        'story': story, 
        'editable': editable, 
        'commentable': story.user_may_comment(request.user),
        'addableBooks': addableBooks,
        'feedback_mode': feedback_mode,
        'feedback_readonly': feedback_readonly,
        'is_teacher': teacher_has_feedback_access,
        'is_story_author': is_story_author,
        'prompt_name': prompt_name,
        'draft_feedback': draft_feedback,
        'latest_teacher_feedback': latest_teacher_feedback,
        'latest_student_reply': latest_student_reply,
        'latest_feedback_thread': latest_feedback_thread,
        'feedback_history_comments': feedback_history_comments,
    })

def show_json(request, story_id):
    story = Story.objects.get_for_request_or_404(request, pk=story_id)
    return JsonResponse(story.for_json())

def show_ink(request, story_id):
    story = Story.objects.get_for_request_or_404(request, pk=story_id)
    return render(request, 'unfold_studio/show_ink.html', {'story': story})

def signup(request):
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
                            # Verify the code exists and isn't used
                            join_code = JoinCode.objects.get(code=code_str, assigned_user__isnull=True)
                            
                            # Link student to the group
                            user.literacy_groups.add(join_code.group)
                            
                            # Claim the code
                            join_code.assigned_user = user
                            join_code.save()
                            
                            log.info(event="Student Sign Up Successful", arg={"user": user.username})
                            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                            return redirect('home')

                        except JoinCode.DoesNotExist:
                            # Manually trigger a failure to roll back the user creation
                            raise ValueError("Invalid or expired join code.")

                    elif role == 'teacher':
                        messages.info(request, 
                        f"Account created! To gain instructor access, please contact Dr. Chris Proctor at chrisp@buffalo.edu to request access."
                        f"Include your username: {user.username}, name, institution, and how you plan to use Unfold Studio. Until then, you can use the site as a regular user. "
                        f"Once approved, your account will be upgraded to instructor status")
                        log.info(event="Teacher Sign Up (Pending)", arg={"user": user.username})
                        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                        return redirect('home')

                    else: # Regular User
                        log.info(event="New User Sign Up", arg={"user": user.username})
                        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                        return redirect('home')

            except ValueError as e:
                messages.error(request, str(e))
                # The transaction.atomic() ensures the User object is deleted if this happens
                return render(request, 'registration/signup.html', {'form': form})
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

class StoryVersionDetailView(View):
    verb = "viewed the history of"

    def get(self, request, *args, **kwargs):
        self.story = story = Story.objects.get_for_request_or_404(request, pk=kwargs['pk'])
        if not story.author:
            raise Http404()
        vIndex = int(kwargs['version']) # 1-indexed!
        versions = Version.objects.get_for_object(story).exclude(revision__comment__exact='').reverse()
        if vIndex > versions.count() or vIndex < 1:
            raise Http404()
        comment = versions[vIndex - 1].revision.comment
        if len(comment) > 100:
            comment = comment[:100] + '...'
        return render(request, 'unfold_studio/show_story_version.html', {
            'story': versions[vIndex - 1].object,
            'comment': comment,
            'version': vIndex,
            'previousVersion': vIndex - 1 if vIndex > 1 else None,
            'nextVersion': vIndex + 1 if vIndex + 1 <= versions.count() else None
        })

    def get_object(self):
        return self.story

class StoryMethodView(LoginRequiredMixin, SingleObjectMixin, View):
    model = Story
    require_editable = True

    def get_queryset(self):
        if self.require_editable:
            return Story.objects.editable_for_request(self.request)
        else:
            return Story.objects.for_request(self.request)

class LoveStoryView(StoryMethodView):
    require_editable = False
    verb = "loved"
    def post(self, request, *args, **kwargs):
        story = self.get_object()
        if self.request.user.profile in story.loves.all():
            messages.warning(self.request, "You already love '{}'".format(story.title))
        elif self.request.user == story.author:
            messages.warning(self.request, "You can't love your own stories.".format(story.title))
        else:
            story.loves.add(self.request.user.profile)
            LiteracyEvent.objects.create(
                event_type=LiteracyEvent.LOVED_STORY, 
                subject=self.request.user,
                story=story
            )
        return redirect('show_story', story.id)
        
class ForkStoryView(StoryMethodView):
    require_editable = False
    verb = "forked"
    def post(self, request, *args, **kwargs):
        parent = self.get_object()
        if not request.user.is_authenticated:
            messages.warning(request, "You must be logged in to fork stories")
            return redirect('show_story', parent.id)
        story = Story(
            author=request.user, 
            parent=parent,
            title="{} (fork)".format(parent.title),
            ink=parent.ink,
            creation_date=now(), 
            edit_date=now(), 
        )
        with reversion.create_revision():
            story.save()
            reversion.set_user(story.author)
            if parent.author:
                reversion.set_comment("{} forked from @story:{} by @user:{}".format(story.title, parent.id,
                        parent.author.id))
            else:
                reversion.set_comment("{} forked from @story:{}".format(story.title, parent.id))
        story.compile()
        story.sites.add(get_current_site(self.request))
        #messages.success(self.request, "You have forked '{}'".format(story.title))
        LiteracyEvent.objects.create(
            event_type=LiteracyEvent.FORKED_STORY,
            subject=request.user,
            story=story
        )
        return redirect('show_story', story.id)

class DeleteStoryView(StoryMethodView):
    verb = "deleted"
    def post(self, request, *args, **kwargs):
        story = self.get_object()
        if not request.user.is_authenticated:
            messages.warning(request, "You need to be logged in to delete stories")
            return redirect('show_story', parent.id) 
        if story.author != request.user:
            messages.warning(request, "You can only delete your own stories")
            return redirect('show_story', story.id)
        messages.success(request, "Deleted '{}'".format(story.title))
        for prompt in story.prompts_submitted.all():
            story.prompts_submitted.remove(prompt)
        for book in story.books.all():
            story.books.remove(book)
        story.deleted = True
        story.save()
        return redirect('show_user', request.user.username)
        
class ShareStoryView(StoryMethodView):
    verb = "shared"
    def post(self, request, *args, **kwargs):
        story = self.get_object()
        if story.author != request.user:
            messages.warning(request, "You can only share your own stories.")
        elif story.shared:
            messages.warning(request, "'{}' is already shared.".format(story.title))
        else:
            story.shared = True
            story.save()
            #messages.success(request, "You shared '{}'".format(story.title))
            LiteracyEvent.objects.create(
                event_type=LiteracyEvent.PUBLISHED_STORY,
                subject=request.user,
                story=story
            )
        return redirect('show_story', story.id)

class UnshareStoryView(StoryMethodView):
    verb = "unshared"
    def post(self, request, *args, **kwargs):
        story = self.get_object()
        if story.author != request.user:
            messages.warning(request, "You can only unshare your own stories.")
        elif not story.shared:
            messages.warning(request, "'{}' is not shared.".format(story.title))
        else:
            story.shared = False
            story.save()
            LiteracyEvent.objects.create(
                event_type=LiteracyEvent.UNPUBLISHED_STORY,
                subject=request.user,
                story=story
            )
            #messages.success(request, "You unshared '{}'".format(story.title))
        return redirect('show_story', story.id)

class NewStoryVersionView(StoryMethodView):
    verb = "created a new version of"
    template = "unfold_studio/new_story_version.html"

    def get(self, request, *args, **kwargs):
        story = self.get_object()
        version = Version.objects.get_for_object(story).first()
        form = StoryVersionForm(initial={'comment': version.revision.comment})
        return render(request, self.template, {'form': form, 'story': story})

    def post(self, request, *args, **kwargs):
        form = StoryVersionForm(request.POST)
        story = self.get_object()
        if form.is_valid():
            version = Version.objects.get_for_object(story).first()
            revision = version.revision
            revision.comment = form.cleaned_data['comment']
            revision.save()
            LiteracyEvent.objects.create(
                event_type=LiteracyEvent.TAGGED_STORY_VERSION,
                subject=request.user,
                story=story
            )
            return redirect('show_story_versions', story.id)
        else:
            return render(request, self.template, {'form': form, 'story': story})

class StoryVersionListView(DetailView):
    model = Story
    template_name = "unfold_studio/story_version_list.html"
    context_object_name = 'story'

    def get_queryset(self):
        return Story.objects.for_request(self.request)

    def get(self, request, *args, **kwargs):
        story = self.get_object()
        if not story.author:
            raise Http404()
        if not story.user_may_comment(self.request.user):
            messages.warning(request, "You can only comment on a story if its author follows you or if they submit the story to one of your prompts.")
        if self.request.user == story.author:
            messages.success(request, "Tip: If you unfollow a user, their comments will disappear.")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        story = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid() and story.user_may_comment(request.user):
            comment = Comment.objects.create(
                author = request.user,
                story = story,
                message = form.cleaned_data['comment']
            )
            log.info("{} commented on {}".format(request.user, story))
            LiteracyEvent.objects.create(
                event_type=LiteracyEvent.COMMENTED_ON_STORY,
                subject=request.user,
                story=story
            )
            return redirect('show_story_versions', story.id)
        else:
            return redirect('show_story_versions', args=[story.id])
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        story = self.get_object()
        versions = Version.objects.get_for_object(story).exclude(revision__comment__exact='').reverse().annotate(
                index=Window(RowNumber()))

        comments = Comment.objects.for_story(story).all()

        def date(e):
            if isinstance(e, Comment):
                d = e.creation_date
            elif isinstance(e, Version):
                d = e.revision.date_created
            else:
                raise ValueError("Unexpected value: {}".format(e))
            if timezone.is_naive(d):
                d = timezone.make_aware(d)
            return d

        history = sorted(list(versions) + list(comments), key=date)
        context['history'] = [
            {
                'content': 'version' if isinstance(e, Version) else 'comment',
                'object': e
            }
            for e in history
        ]

        feedback_prompt = story.prompts_submitted.filter(
            literacy_group__leaders=self.request.user,
            deleted=False
        ).distinct().first()

        context['feedback_prompt'] = feedback_prompt

        if feedback_prompt:
            context['skip_url'] = reverse(
                'show_prompt',
                args=[feedback_prompt.literacy_group.id, feedback_prompt.id]
            )
        else:
            context['skip_url'] = reverse('show_story', args=[story.id])

        if story.user_may_comment(self.request.user):
            form = CommentForm()
            form.fields['comment'].label = "COMMENTS"
            form.fields['comment'].widget.attrs.update({
                'class': 'feedback-textarea',
                'placeholder': 'Write feedback for the student here...',
                'rows': 8,
                'autocomplete': 'off',
            })
            context['commentForm'] = form

        return context

class CreateBookView(LoginRequiredMixin, CreateView):
    model = Book
    fields = ['title', 'description']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['header'] = "Create a new book"
        return context

    def post(self, request, *args, **kwargs):
        _book = Book(owner=request.user)
        form = self.get_form_class()(request.POST, instance=_book)
        if form.is_valid():
            book = form.save()
            book.sites.add(get_current_site(request))
            LiteracyEvent.objects.create(
                event_type=LiteracyEvent.PUBLISHED_BOOK,
                subject=request.user,
                book=book
            )
            log.info("{} created book {} (id {})".format(request.user, book.title, book.id))
            return redirect('show_book', book.id)
        else:
            context = self.get_context_data(form=form)
            return render('book_form', context)

class BookListView(ListView):
    model = Book

    def get_queryset(self):
        return Book.objects.filter(sites__id=get_current_site(self.request).id).select_related('owner')

class BookDetailView(DetailView):
    # TODO: Use this as a model for using Mixins. get_context_data is needlessly verbose.
    model = Book

    def get_queryset(self):
        return Book.objects.filter(sites__id=get_current_site(self.request).id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user if self.request.user.is_authenticated else None
        context['stories'] = self.get_object().stories.for_request(self.request).select_related('author').prefetch_related('loves')
        return context

class UpdateBookView(UpdateView):
    model = Book
    fields = ['title', 'description']

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Book.objects.for_request(self.request).filter(owner=self.request.user)
        else:
            raise Http404()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['header'] = "Edit {}".format(self.object.title)
        return context

    def get_success_url(self):
        return reverse('show_book', args=(self.object.id,))

class AddStoryToBookView(LoginRequiredMixin, StoryMixin, DetailView):
    def post(self, request, *args, **kwargs):
        book = self.get_object(Book.objects.filter(owner=request.user))
        story = self.get_story()    # Lookup defaults to using story_id URL kwarg
        if story in book.stories.all():
            messages.warning(self.request, "{} is already in {}".format(story.title, book.title))
            log.warning("{} tried to re-add {} ({}) to book {} ({})".format(
                    u(request), story.title, story.id, book.title, book.id))
        else:
            book.stories.add(story)
            messages.success(self.request, "You added {}".format(story.title))
            log.info("{} added {} ({}) to book {} ({})".format(
                    u(request), story.title, story.id, book.title, book.id))
            LiteracyEvent.objects.create(
                event_type=LiteracyEvent.ADDED_STORY_TO_BOOK,
                subject=request.user,
                story=story,
                book=book
            )
        return redirect('show_book', book.id)
            
class RemoveStoryFromBookView(LoginRequiredMixin, StoryMixin, DetailView):
    def post(self, request, *args, **kwargs):
        book = self.get_object(Book.objects.filter(owner=request.user))
        story = self.get_story(queryset=book.stories.all())    # Lookup defaults to using story_id URL kwarg
        book.stories.remove(story)
        messages.success(self.request, "You removed {}".format(story.title))
        log.info("{} removed {} ({}) from book {} ({})".format(
                u(request), story.title, story.id, book.title, book.id))
        LiteracyEvent.objects.create(
            event_type=LiteracyEvent.REMOVED_STORY_FROM_BOOK,
            subject=request.user,
            story=story,
            book=book
        )
        return redirect('show_book', book.id)

class CreateStoryPlayInstanceView(CreateView):

    def post(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        user_id = user.id if user else None
        request_body = json.loads(request.body)

        story_id = request_body['story_id']

        story_play_instance = StoryPlayInstance.objects.create(
            user_id=user_id,
            story_id=story_id
        )

        return JsonResponse({"story_play_instance_uuid": str(story_play_instance.uuid)})


class CreateStoryPlayRecordView(CreateView):

    def post(self, request, *args, **kwargs):
        request_body = json.loads(request.body)

        story_play_instance_uuid = request_body['story_play_instance_uuid']
        data_type = request_body['data_type']
        data = request_body['data']
        story_point = request_body['story_point']

        story_play_instance = StoryPlayInstance.objects.get(uuid=story_play_instance_uuid)

        story_play_record = StoryPlayRecord.objects.create(
            story_play_instance=story_play_instance,
            data_type=data_type,
            data=data,
            story_point=story_point,
        )

        return JsonResponse({"story_play_record_uuid": str(story_play_record.uuid)})

def require_entry_point(request):
    return render(request, 'unfold_studio/require_entry_point.js', content_type="application/javascript")

def embed_entry_point(request):
    return render(request, 'unfold_studio/embed_entry_point.js', content_type="application/javascript")

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
