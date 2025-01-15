from django.db import models 
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from profiles.models import Profile
import reversion
from django.conf import settings
import json
import re
import logging
from collections import OrderedDict, deque
from enum import Enum
import os
import subprocess
import math
from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site
from django.http import Http404                         
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex

log = logging.getLogger(__name__)

class StoryManager(models.Manager):
    """
    Extends the default manager with custom queries. Note that "for request"
    methods will check for user authentication as a convenience, even though
    it's not really the model's business.

    Methods for site and user will not check authentication, and will raise errors
    if called with an anonymous user.
    """

    def valid(self):
        "Returns non-deleted objects"
        return self.get_queryset().filter(
            Q(public=True) | Q(author__is_active=True),
            deleted=False
        )

    def for_site(self, site):
        """
        Returns only stories in the current scope--that is, those associated with a site and 
        not deleted.
        """
        return self.valid().filter(sites=site)

    def for_request(self, request):
        "Returns stories which are visible to the current request"
        user = request.user
        site = get_current_site(request)
        if user.is_authenticated:
            return self.for_site_user(site, user)
        else:
            return self.for_site_anonymous_user(site)

    def for_site_user(self, site, user):
        return self.for_site(site).filter(
            Q(shared=True) | 
            Q(public=True) |
            Q(prompts_submitted__literacy_group__leaders=user) |
            Q(author=user)
        ).distinct()

    def for_site_anonymous_user(self, site):
        return self.for_site(site).filter(
            Q(public=True) | Q(shared=True)
        )

    def editable_for_request(self, request):
        "Returns stories which are visible to the current request"
        user = request.user
        site = get_current_site(request)
        if user.is_authenticated:
            return self.editable_for_site_user(site, user)
        else:
            return self.editable_for_site_anonymous_user(site)

    def editable_for_site_user(self, site, user):
        return self.for_site(site).filter(
            Q(public=True) |
            Q(author=user)
        )

    def editable_for_site_anonymous_user(self, site):
        return self.for_site(site).filter(
            Q(public=True)
        )

    def get_for_request_or_404(self, request, **kwargs):
        try:
            return self.for_request(request).get(**kwargs)
        except (Story.DoesNotExist, Story.MultipleObjectsReturned):
            raise Http404

    def get_editable_for_request_or_404(self, request, **kwargs):
        try:
            return self.editable_for_request(request).get(**kwargs)
        except (Story.DoesNotExist, Story.MultipleObjectsReturned):
            raise Http404

@reversion.register()
class Story(models.Model):
    """
    Stories can be saved even if invalid.

    """
    title = models.CharField(max_length=400)
    author = models.ForeignKey(User, related_name='stories', blank=True, null=True, on_delete=models.SET_NULL)
    creation_date = models.DateTimeField('date created')
    edit_date = models.DateTimeField('date changed')
    ink = models.TextField(blank=True)
    json = models.TextField(null=True, blank=True)
    shared=models.BooleanField(default=False)
    public=models.BooleanField(default=False)
    featured=models.BooleanField(default=False)
    loves = models.ManyToManyField(Profile, related_name="loved_stories", blank=True)
    parent = models.ForeignKey("unfold_studio.Story", related_name="children", 
            null=True, blank=True, on_delete=models.SET_NULL)
    includes = models.ManyToManyField("unfold_studio.Story", related_name="included_by", blank=True)
    deleted = models.BooleanField(default=False)
    priority = models.FloatField(default=0)
    sites = models.ManyToManyField(Site)
    search = SearchVectorField(null=True)

    objects = StoryManager()

    def visible_to_user(self, user):
        return (
            self.public or self.shared or user == self.author or 
            self.prompts_submitted.filter(literacy_group__leaders=user).exists()
        )

    def user_may_comment(self, user):
        return user.is_authenticated and (
            user == self.author or 
            (self.author and self.author.profile.following.filter(pk=user.profile.pk).exists()) or 
            self.prompts_submitted.filter(literacy_group__leaders=user).exists()
        ) 

    class PreprocessingError(Exception):
        "Raised when something goes wrong during preprocessing."
        def __init__(self, error_type, line=None, message=None):
            self.error_type = error_type
            self.line = line
            self.message = message

    class CompileError(Exception):
        pass
                
    def __str__(self):
        return "{} by {}".format(self.title, self.author)

    def latest_version(self):
        return reversion.models.Version.objects.get_for_object(self).first()

    def compile(self):
        """
        Completes a preprocessing step and then a compile step.
        Sets relevant properties, including json and errors.
        """
        self.errors.clear()
        try:
            ink, i, v, k, offset = self.preprocess_ink()
            self.preprocessed_ink = ink # TODO DEBUG
            
            self.ink_to_json(ink, offset=offset)
            self.includes.set(Story.objects.get(pk=pk) for pk in i.keys())
        except Story.PreprocessingError as e:
            self.errors.create(
                story_version=self.latest_version(),
                error_type=e.error_type.value,
                line=e.line,
                message=e.message
            )
            self.json = None
            self.includes.clear()
        except Story.CompileError:
            # One or more errors will already have been set
            self.json = None
            self.includes.clear()

    @classmethod
    def get_for_inclusion(cls, includeKey, line_number=None):
        "Returns a story's inclusions, variables and knots, ready to include in another story"
        try: 
            pk=int(includeKey) 
            story = Story.objects.get(Q(public=True) | Q(shared=True), pk=pk)
        except ValueError:
            raise Story.PreprocessingError(
                StoryError.ErrorTypes.PREPROCESS_INCLUDE_BAD_KEY, line=line_number,
                message="{} is not a valid story id".format(includeKey)
            )
        except Story.DoesNotExist:
            raise Story.PreprocessingError(
                StoryError.ErrorTypes.PREPROCESS_INCLUDE_STORY_NOT_FOUND, line=line_number,
                message="Could not find story {}. Maybe it's not shared?".format(includeKey)
            )
        if story.errors.exists():
            raise Story.PreprocessingError(
                StoryError.ErrorTypes.PREPROCESS_INCLUDE_STORY_HAS_ERRORS, line=line_number,
                message="Story {} cannot be included because it has errors".format(includeKey)
            )
            raise Story.IncludeError("Story {} is not compiled".format(pk))

        text, i, v, k, offset = story.preprocess_ink()
        return i, v, k
        
    # Note: /* */ style comments not supported.
    def preprocess_ink(self):
        """
        Resolves INCLUDES of other stories, importing knots and variables 
        initializations. However, does not re-define any knots or variables
        already defined in the story, and does not import preamble behavior
        (any instructions before the first knot).
        """
        directInclusions = self.get_inclusions()
        inclusions = OrderedDict(directInclusions.items())
        variables = self.get_variable_initializations()
        initialVarLength = len(variables)
        knots = self.get_knots()
    
        def include(base, new):
            for key, (lineNum, value) in new.items():
                if key not in base.keys():
                    base[key] = (None, value)

        for includeKey in directInclusions.keys():
            iInclusions, iVars, iKnots = Story.get_for_inclusion(includeKey)
            include(inclusions, iInclusions)
            include(variables, iVars)
            include(knots, iKnots)

        

        inkText = "\n".join(
            self.external_function_declarations() +  # call-outs to javascript
            [l for i, l in variables.values()] +    # lifted variable initializations
            self.get_ink_preamble().split('\n') +   # Any remaining preamble (stripped)
            [k for i, k in knots.values()]          # The text of the story's knots
        )
        offset = ((len(variables) - initialVarLength) + len(directInclusions) -
                len(self.external_function_declarations()))
        return inkText, inclusions, variables, knots, offset

    def external_function_declarations(self):
        """
        Declares available external functions. These ought to be bound by the client-side ink player.
        """
        return [
            "EXTERNAL random()",
            "EXTERNAL random_integer(a,b)",
            "EXTERNAL ln(a)",
            "EXTERNAL log2(a)",
            "EXTERNAL round(a)",
            "EXTERNAL floor(a)",
            "EXTERNAL ceiling(a)",
            "EXTERNAL random_gaussian(a, b)",
            "EXTERNAL generate(a)",
            "EXTERNAL input(a,b)",
        ]

    def ink_to_json(self, ink, offset=0):
        """
        Compiles ink code to JSON via an external call to inklecate. 
        Story must be pre-saved so it has an id. Populates self.json; 
        if there are errors, creates StoryErrors.
        """
        fn = "{}.ink".format(self.id)
        fqn = os.path.join(settings.INK_DIR, fn)
        with open(fqn, 'w', encoding='utf-8') as inkfile:
            inkfile.write(ink)
        try:
            warnings = subprocess.check_output([settings.INKLECATE, fqn]).decode("utf-8-sig")
            for warning in warnings.split('\n'):
                if warning.strip():
                    self.create_inklecate_error(warning, offset)
            with open(fqn + ".json", encoding="utf-8-sig") as outfile:
                self.json = outfile.read()
        except subprocess.CalledProcessError as e:
            errors = e.output.decode("utf-8")
            for error in errors.split('\n'):
                if error.strip():
                    self.create_inklecate_error(error, offset)
            self.json = None
        if self.errors.exists():
            raise Story.CompileError()

    def create_inklecate_error(self, line, offset=0):
        try:
            errLevel, location, *description = line.split(":")
            description = ":".join(description)
            lineNum = StoryError.parse_line(location) + offset
        except ValueError:
            log.error("UNREADABLE ERROR:"+line)
            description = "unknown error"
            lineNum = None
        self.errors.create(
            story_version=self.latest_version(),
            error_type=StoryError.classify(description).value,
            line=lineNum,
            message=("line {}: ".format(lineNum) if line else "") + description
        )

    include_pattern = r"^\s*INCLUDE\s+(\d+)\s*(\/\/.*)?(#.*)?$"
    var_init_pattern = r"^\s*(VAR|CONST|LIST)\s+(\w+)\s*="
    knot_pattern = r"^\s*===\s*([\w\d]+)\s*(\(.*\)\s*)?(===)?\s*(\/\/.*)?(#.*)?$"

    def get_inclusions(self):
        "Return an OrderedDict of include codes"
        inclusions = OrderedDict()
        for lineNum, line in enumerate(self.get_ink_preamble(stripped=False).split("\n")):
            result = re.match(self.include_pattern, line)
            if result: 
                inclusions[result.group(1)] = (lineNum+1, line)
        return inclusions

    def get_variable_initializations(self):
        "Returns an OrderedDict of variable name -> initialization line"
        variableInits = OrderedDict()
        for lineNum, line in enumerate(self.get_ink_preamble(stripped=False).split("\n")):
            result = re.match(self.var_init_pattern, line)
            if result:
                variableInits[result.group(2)] = (lineNum+1, line)
        return variableInits

    def get_ink_preamble(self, stripped=True):
        "Returns the content before the first knot"
        try:
            _, _, preamble = next(self.knot_reader(with_preamble=True))
        except StopIteration:
            return ""
        if stripped:
            strippable = [self.include_pattern, self.var_init_pattern]
            condition = lambda l: not any(re.match(p, l) for p in strippable)
            return "\n".join(filter(condition, preamble.split('\n')))
        else:
            return preamble

    def knot_reader(self, with_preamble=False):
        """A generator which iterates through the knots in a story. 
        The preamble is anything before the first knot"""
        currentKnotName = None
        currentKnot = []
        for lineNum, line in enumerate(self.ink.split("\n")):
            newKnot = re.match(self.knot_pattern, line)
            if newKnot:
                if currentKnotName or with_preamble:
                    yield(lineNum, currentKnotName, "\n".join(currentKnot))
                currentKnotName = newKnot.group(1)
                currentKnot = [line]
            else:
                currentKnot.append(line)
        if currentKnotName and any(currentKnot):
             yield(lineNum, currentKnotName, "\n".join(currentKnot))
        if with_preamble and currentKnotName is None:
            yield(0, None, "\n".join(currentKnot))

    def get_knots(self, with_preamble=False):
        return OrderedDict((name, (lineNum, knot)) for (lineNum, name, knot) 
                in self.knot_reader(with_preamble=with_preamble))
                
    # Using Hacker News gravity algorithm: 
    # https://medium.com/hacking-and-gonzo/how-hacker-news-ranking-algorithm-works-1d9b0cf2c08d
    def update_priority(self):
        self.priority = self.score() / pow(self.age_in_hours() + 2, settings.STORY_PRIORITY['GRAVITY'])

    def score(self):
        return (1 + 
            self.loves.count() * settings.STORY_PRIORITY['LOVE_SCORE'] + 
            self.books.count() * settings.STORY_PRIORITY['BOOK_SCORE'] + 
            self.children.filter(~Q(author=self.author)).count() * settings.STORY_PRIORITY['FORK_SCORE'] + 
            self.includes.count() * settings.STORY_PRIORITY['INCLUDES_SCORE'] + 
            self.included_by.count() * settings.STORY_PRIORITY['INCLUDED_BY_SCORE'] + 
            int(self.errors.exists()) * settings.STORY_PRIORITY['ERRORS_SCORE'] + 
            int(self.featured) * settings.STORY_PRIORITY['FEATURED_SCORE'])

    def age_in_hours(self):
        return (timezone.now() - self.edit_date).total_seconds() / (60 * 60)

    def for_json(self):
        "Returns JSON for the story in old format. Needs to be updated once the "
        return {
            "id": self.id,
            "compiled": json.loads(self.json) if self.json else None,
            "ink": self.ink,
            "status": "error" if self.errors.exists() else "ok",
            "error": "; ".join(e.message for e in self.errors.all()),
            "error_line": self.errors.first().line if self.errors.exists()  and self.errors.first() else 0,
            "author": self.author.username if self.author else None
        }

    class Meta:
        ordering = ['-priority']
        verbose_name_plural = "Stories"
        indexes = [
            GinIndex(fields=['search']),
        ]
    

class BookManager(models.Manager):
    def valid(self):
        "Returns non-deleted objects"
        return self.get_queryset().filter(deleted=False)

    def for_site(self, site):
        """
        Returns only books in the current scope--that is, those associated with a site and not deleted.
        """
        return self.valid().filter(sites=site)

    def for_request(self, request):
        "Returns books which are visible to the current request"
        site = get_current_site(request)
        return self.for_site(site)

class Book(models.Model):
    title = models.CharField(max_length=400)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='books')
    stories = models.ManyToManyField(Story, related_name='books')
    sites = models.ManyToManyField(Site)
    priority = models.FloatField(default=0)
    deleted = models.BooleanField(default=False)

    objects = BookManager()

    def update_priority(self):
        self.priority = self.score()

    def score(self):
        stories = self.stories.all()
        return (1 + 
            math.log(1 + len(stories)) * settings.BOOK_PRIORITY['LOG_NUM_STORIES'] + 
            (stories[len(stories) // 2].priority if any(stories) else 0) * 
                    settings.BOOK_PRIORITY['MEDIAN_STORY_PRIORITY']
        )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-priority']

class StoryError(models.Model):

    class ErrorTypes(Enum):
        PREPROCESS_ERROR = 100
        PREPROCESS_INCLUDE_BAD_KEY = 101
        PREPROCESS_INCLUDE_STORY_NOT_FOUND = 102
        PREPROCESS_INCLUDE_STORY_HAS_ERRORS = 103
        COMPILE_ERROR = 200
        COMPILE_SYNTAX_KNOT_NAME = 201
        COMPILE_SYNTAX_VAR_INCREMENT = 220
        COMPILE_MISSING_DIVERT_TARGET = 260
        RUNTIME_WARNING = 400
        RUNTIME_LOOSE_END = 401
        OTHER = 0

    story = models.ForeignKey(Story, null=True, blank=True, on_delete=models.SET_NULL, related_name='errors')
    story_version = models.ForeignKey(reversion.models.Version, on_delete=models.CASCADE)
    error_type = models.IntegerField(choices=[(t.value, t.name) for t in ErrorTypes], default=0)
    line = models.IntegerField(blank=True, null=True)
    message = models.CharField(max_length=400, null=True, blank=True)

    patterns = {
        "Divert target not found": ErrorTypes.COMPILE_MISSING_DIVERT_TARGET,
        "variable for increment could not be found": ErrorTypes.COMPILE_SYNTAX_VAR_INCREMENT,
        "Apparent loose end exists": ErrorTypes.RUNTIME_LOOSE_END
    }

    class Meta:
        ordering = ['line']

    @classmethod
    def classify(cls, error_description):
        "Maps string -> Error Type"
        for pattern, error in cls.patterns.items():
            if re.search(pattern, error_description): return error
        return StoryError.ErrorTypes.OTHER

    @classmethod
    def parse_line(cls, error_location):
        result = re.search(r"line (\d+)", error_location)
        if result: return int(result.group(1))

    



