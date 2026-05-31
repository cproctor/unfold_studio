import json
import re

from django.shortcuts import render, redirect
from django.http import Http404
from django.views import View
from django.views.generic.detail import SingleObjectMixin, DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from django import forms
from django.forms import ModelForm
from django.conf import settings as s
import structlog

from books.models import Book
from stories.mixins import StoryMixin
from stories.forms import GenreTagField
from stories.genres import get_top_genres, genre_label
from literacy_events.models import LiteracyEvent

log = structlog.get_logger("books")


class BookForm(ModelForm):
    genres = GenreTagField()

    class Meta:
        model = Book
        fields = ['title', 'description', 'genres']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.initial['genres'] = self.instance.genres or []


def u(request):
    return request.user.username if request.user.is_authenticated else "<anonymous>"


class CreateBookView(LoginRequiredMixin, CreateView):
    model = Book
    form_class = BookForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['header'] = "Create a new book"
        return context

    def post(self, request, *args, **kwargs):
        _book = Book(owner=request.user)
        form = BookForm(request.POST, instance=_book)
        if form.is_valid():
            book = form.save(commit=False)
            book.genres = form.cleaned_data.get('genres', [])
            book.save()
            LiteracyEvent.objects.create(
                event_type=LiteracyEvent.PUBLISHED_BOOK,
                subject=request.user,
                book=book
            )
            log.info("{} created book {} (id {})".format(request.user, book.title, book.id))
            return redirect('show_book', book.id)
        else:
            context = self.get_context_data(form=form)
            return render(request, 'unfold_studio/book_form.html', context)


class BookListView(ListView):
    model = Book

    def get_queryset(self):
        qs = Book.objects.all().select_related('owner').prefetch_related('stories')
        query = self.request.GET.get('query', '').strip()
        if query:
            qs = qs.filter(
                Q(title__icontains=query) | Q(owner__username__icontains=query) | Q(description__icontains=query)
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        genre_filter = self.request.GET.get('genre', '')
        query = self.request.GET.get('query', '').strip()
        all_books = list(context['object_list'])

        top_genres = get_top_genres(Book.objects.all(), s.GENRE_BROWSE_TAG_COUNT)
        genre_choices = [(g, genre_label(g)) for g in top_genres]

        if query:
            if genre_filter == 'other':
                search_results = [b for b in all_books if not b.genres]
            elif genre_filter:
                search_results = [b for b in all_books if genre_filter in (b.genres or [])]
            else:
                search_results = all_books
            context['genre_groups'] = {}
            context['ungenred_books'] = []
            context['search_results'] = search_results
            context['genre_choices'] = genre_choices
            context['active_genre'] = genre_filter
            context['query'] = query
            context['is_search'] = True
            return context

        if genre_filter == 'other':
            all_books = [b for b in all_books if not b.genres]
        elif genre_filter:
            all_books = [b for b in all_books if genre_filter in (b.genres or [])]

        genre_groups = {}
        ungenred = []
        for book in all_books:
            if book.genres:
                for g in book.genres:
                    if genre_filter and genre_filter != 'other' and g != genre_filter:
                        continue
                    genre_groups.setdefault(genre_label(g), []).append(book)
            else:
                ungenred.append(book)

        context['genre_groups'] = genre_groups
        context['ungenred_books'] = ungenred
        context['search_results'] = []
        context['genre_choices'] = genre_choices
        context['active_genre'] = genre_filter
        context['query'] = query
        context['is_search'] = False
        return context


class BookDetailView(DetailView):
    model = Book

    def get_queryset(self):
        return Book.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stories = self.get_object().stories.for_request(self.request).select_related('author').prefetch_related('loves')
        stories_with_snippets = [(s, self._extract_snippet(s)) for s in stories]
        context['stories'] = stories
        context['stories_with_snippets'] = stories_with_snippets
        return context

    def _extract_snippet(self, story):
        desc = (story.description or "").strip()
        if not story.json:
            return desc
        try:
            compiled = json.loads(story.json)
        except Exception:
            return desc
        chunks = []

        def walk(node):
            if len(chunks) >= 12:
                return
            if isinstance(node, str):
                s = node.strip()
                if s.startswith("^"):
                    s = s.lstrip("^").strip()
                    s = re.sub(r"\s+", " ", s)
                    if s:
                        chunks.append(s)
            elif isinstance(node, list):
                for item in node:
                    walk(item)
            elif isinstance(node, dict):
                for v in node.values():
                    walk(v)

        walk(compiled)
        snippet = " ".join(chunks)
        if len(snippet) > 300:
            snippet = snippet[:297] + "..."
        return snippet or desc


class UpdateBookView(UpdateView):
    model = Book
    form_class = BookForm

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
        story = self.get_story()
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
        story = self.get_story(queryset=book.stories.all())
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
