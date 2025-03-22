from locust import HttpUser, task, between, events
from gevent.lock import Semaphore
import re, os, random
from datetime import datetime

today_date = datetime.now().strftime('%Y-%m-%d')
summary_file = '../.unfold_studios/loadtest_metadata/summaries/summary_{}.txt'.format(today_date)
summary_file_lock = Semaphore()

all_users = []
user_count_lock = Semaphore()

public_stories = {}
public_stories_lock = Semaphore()

@events.quitting.add_listener
def _(environment, **kwargs):
    print("👋 Locust is shutting down. Running cleanup tasks...")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("🔥 All users have stopped running tasks")
    print("🔥 Printing anonymous user stories into summary file...")
    with open(summary_file, 'a') as summary:
        summary.write("\n################################################################\n")
        summary.write("Anonymous Stories\n")
        anonymous_stories = ["{} : {}".format(key, value.get("title")) 
                             for key, value in public_stories.items() 
                             if value.get("user") == "anonymous"
                             ]
        summary.write(','.join(anonymous_stories))


class BaseUser(HttpUser):
    wait_time = between(1, 3)
    abstract = True
    ink_folder = '../.unfold_studios/loadtest_metadata/ink/'
    def get_random_ink_file(self):
        files = [f for f in os.listdir(self.ink_folder) if os.path.isfile(os.path.join(self.ink_folder, f))]
        
        selected_file = random.choice(files)
        with open(os.path.join(self.ink_folder, selected_file), 'r', encoding='utf-8') as file:
            return file.read()
        
    def get_csrf_token(self, response):
        csrf_token_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
        return csrf_token_match.group(1)
    
    def get_csrf_token_from_cookie(self, response):
        csrf_token = response.cookies.get('csrftoken')
        return csrf_token
    
    def get_random_user_name(self):
        random_number = random.randint(1, 1000000)
        return "user_{}".format(random_number)
    
    def get_random_story_name(self):
        random_number = random.randint(1, 1000000)
        return "test_story_{}".format(random_number)
    
    def get_random_book_name(self):
        random_number = random.randint(1, 1000000)
        return "test_book_{}".format(random_number)
    
class UnfoldStudioAnonymousUser(BaseUser):
    weight = 1
    @task(2)
    def home_page(self):
        self.client.get("/", name="Anonymous Home Page (/)")

    @task(2)
    def list_story_page(self):
        self.client.get('/stories', name="Anonymous list stories (/stories)")

    @task(2)
    def list_books_page(self):
        self.client.get('/books', name="Anonymous list books (/books)")

    @task(1)
    def create_new_story(self):
        response = self.client.get('/stories/new', name="Anonymous New Story Title/Description (/stories/new)")
        if response.status_code != 200: return

        title = self.get_random_story_name()

        form_data = {
            "csrfmiddlewaretoken": self.get_csrf_token(response),
            "title": title,
            "description": "Story used for load testing"
        }
        
        response = self.client.post(
            '/stories/new/', 
            data=form_data, 
            allow_redirects=False, 
            headers={
                "Referer": response.url
            },
            name="Anonymous New Story Title/Description (/stories/new)")
        if response.status_code != 302: return
        story_id = response.headers.get('Location').split('/')[-2]

        global public_stories
        with public_stories_lock:
            public_stories[story_id] = {
                "user": "anonymous",
                "title": title
            }

    @task(2)
    def edit_story(self):
        anonymous_stories = [key for key, value in public_stories.items() if value.get("user") == "anonymous"]
        if len(anonymous_stories) == 0: return
        story_id = random.choice(anonymous_stories)
        response = self.client.get('stories/{}/'.format(story_id), name="Anonymous Edit Story (/stories/<story_number>/)")
        if response.status_code != 200 : return

        ink_content = self.get_random_ink_file()
        form_data = {
            "ink": ink_content
        }

        self.client.post(
            'stories/{}/compile/'.format(story_id), 
            data=form_data,
            cookies={"csrftoken": self.get_csrf_token_from_cookie(response)},
            headers={
                "X-CSRFToken": self.get_csrf_token_from_cookie(response),
                "Referer": response.url
            },
            name="Anonymous compile edited story (/stories/<story_number>/compile/)"
            )
        
    @task(1)
    def view_story(self):
        if len(public_stories) == 0: return
        story_id = random.choice(list(public_stories.keys()))
        self.client.get('stories/{}/'.format(story_id), name="Anonymous View Story (/stories/<story_number>)")

class UnfoldStudioAuthenticatedUser(BaseUser):
    weight = 9

    def on_start(self):
        self.signed_up = False
        self.username = self.get_random_user_name()
        self.password = "Test{}$pwd".format(self.username.split("_")[1])
        
        response = self.client.get('/signup', name="Signup Page")
        if response.status_code != 200: return

        self.csrf_token = self.get_csrf_token(response)

        form_data = {
            "csrfmiddlewaretoken": self.get_csrf_token(response),
            "username": self.username,
            "email": "{}@gmail.com".format(self.username),
            "password1": self.password,
            "password2": self.password
        }

        response = self.client.post(
            '/signup', 
            data=form_data, 
            name="Signup User (/signup)", 
            headers={
                "Referer": response.url
            },
            allow_redirects=False)
        if response.status_code != 302: return

        with user_count_lock:
            all_users.append(self.username)
    
        self.private_stories = {}
        self.private_books = {}
        self.liked_stories = []
        self.following = []

        self.signed_up = True


    @task(10)
    def self_user_page(self):
        if (not self.signed_up): return
        self.client.get('/users/{}'.format(self.username), name="Authenticated User Self Page (/users/<self_user_id>)")

    @task(2)
    def home_page(self):
        if (not self.signed_up): return
        self.client.get("/", name="Authenticated Home Page (/)")

    @task(2)
    def list_story_page(self):
        if (not self.signed_up): return
        self.client.get('/stories', name="Authenticated list stories (/stories)")

    @task(2)
    def list_books_page(self):
        if (not self.signed_up): return
        self.client.get('/books', name="Authenticated list books (/books)")

    @task(8)
    def create_new_story(self):
        if (not self.signed_up): return
        response = self.client.get('/stories/new', name="Authenticated New Story Title/Description (/stories/new)")
        if response.status_code != 200: return

        title = self.get_random_story_name()

        form_data = {
            "csrfmiddlewaretoken": self.get_csrf_token(response),
            "title": title,
            "description": "Story used for load testing"
        }
        
        response = self.client.post(
            '/stories/new/', 
            data=form_data, 
            headers={
                "Referer": response.url
            },
            allow_redirects=False, name="Authenticated New Story Title/Description (/stories/new)")
        if response.status_code != 302: return
        
        story_id = response.headers.get('Location').split('/')[-2]

        self.private_stories[story_id] = {
            "user": self.username,
            "title": title,
            "books": []
        }

    @task(3)
    def create_new_book(self):
        if (not self.signed_up): return
        response = self.client.get('/books/new', name="Authenticated New Book Title/Description (/books/new)")
        if response.status_code != 200: return

        form_data = {
            "csrfmiddlewaretoken": self.get_csrf_token(response),
            "title": self.get_random_book_name(),
            "description": "Book for load testing"
        }
        
        response = self.client.post(
            '/books/new/', 
            data=form_data, 
            headers={
                "Referer": response.url
            },
            allow_redirects=False, name="Authenticated New Book Title/Description (/books/new)")
        if response.status_code != 302: return
        book_id = response.headers.get('Location').split('/')[-2]

        self.private_books[book_id] = {
            "user": self.username,
            "stories": []
        }

    @task(5)
    def edit_story(self):
        if (not self.signed_up): return
        public_stories_keys = [key for key, value in public_stories.items() if value.get("user") == "anonymous"]
        accessible_stories = public_stories_keys + list(self.private_stories.keys())
        if len(accessible_stories) == 0: return
        story_id = random.choice(accessible_stories)
        response = self.client.get('stories/{}/'.format(story_id), name="Authenticated Edit Story (/stories/<story_number>/)")
        if response.status_code != 200: return

        ink_content = self.get_random_ink_file()
        form_data = {
            "ink": ink_content
        }

        self.client.post(
            'stories/{}/compile/'.format(story_id), 
            data=form_data,
            cookies={"csrftoken": self.get_csrf_token_from_cookie(response)},
            headers={
                "X-CSRFToken": self.get_csrf_token_from_cookie(response),
                "Referer": response.url
            },
            name="Authenticated compile edited story (/stories/<story_number>/compile)"
            )
        
    @task(1)
    def view_story(self):
        if (not self.signed_up): return
        accessible_stories = list(public_stories.keys()) + list(self.private_stories.keys())
        if len(accessible_stories) == 0: return
        story_id = random.choice(accessible_stories)
        self.client.get('stories/{}/'.format(story_id), name="Authenticated View Story (/stories/<story_number>)")

    @task(6)
    def share_story(self):
        if (not self.signed_up): return
        if len(self.private_stories.keys()) == 0: return
        story_id = random.choice(list(self.private_stories.keys()))

        response = self.client.get('stories/{}/'.format(story_id), name="Authenticated Share Story (stories/<story_number>/)")
        if response.status_code != 200: return

        form_data = {
            "csrfmiddlewaretoken": self.get_csrf_token(response),
        }

        self.client.post(
            'stories/{}/share/'.format(story_id), 
            data=form_data,
            headers={
                "Referer": response.url
            },
            name="Authenticated Share Story (/stories/<story_number>/share/)")
        private_story = self.private_stories[story_id]

        with public_stories_lock:
            public_stories[story_id] = private_story

        del self.private_stories[story_id]

    @task(6)
    def unshare_story(self):
        if (not self.signed_up): return
        public_stories_keys = [key for key, value in public_stories.items() if value.get("user") == self.username]
        if len(public_stories_keys) == 0: return
        story_id = random.choice(public_stories_keys)

        response = self.client.get('stories/{}/'.format(story_id), name="Authenticated Unshare Story (/stories/<story_number>/)")
        if response.status_code != 200: return

        form_data = {
            "csrfmiddlewaretoken": self.get_csrf_token(response),
        }

        self.client.post(
            'stories/{}/unshare/'.format(story_id), 
            data=form_data, 
            headers={
                "Referer": response.url
            },
            name="Authenticated Unshare Story (/stories/<story_number>/unshare/)")
        private_story = public_stories[story_id]
        self.private_stories[story_id] = private_story

        with public_stories_lock:
            del public_stories[story_id]

    @task(3)
    def delete_story(self):
        if (not self.signed_up): return
        public_stories_keys = [key for key, value in public_stories.items() if value.get("user") == self.username]
        accessible_stories = public_stories_keys + list(self.private_stories.keys())
        if len(accessible_stories) == 0: return

        response = self.client.get('/users/{}'.format(self.username), name="Delete Story Get User (/users/<self_user_number>)")
        if response.status_code != 200: return

        form_data = {
            "csrfmiddlewaretoken": self.get_csrf_token(response),
        }

        story_id = random.choice(accessible_stories)

        self.client.post(
            'stories/{}/delete/'.format(story_id), 
            data=form_data, 
            headers={
                "Referer": response.url
            },
            name="Authenticated Delete Story (/stories/<story_number>/delete)")
        if story_id in self.private_stories: del self.private_stories[story_id]
        else:
            with public_stories_lock:
                del public_stories[story_id]

    @task(6)
    def add_story_to_book(self):
        if (not self.signed_up): return
        if len(self.private_books.keys()) == 0: return
        book_id = random.choice(list(self.private_books.keys()))

        public_stories_keys = [key for key, value in public_stories.items() if value.get("user") == self.username]
        accessible_stories = public_stories_keys + list(self.private_stories.keys())
        if len(accessible_stories) == 0: return
        story_id = random.choice(accessible_stories)


        response = self.client.get('books/{}'.format(book_id), name="Authenticated Add Story to Book (/books/<book_id>)")
        if response.status_code != 200: return

        form_data = {
            "csrfmiddlewaretoken": self.get_csrf_token(response),
        }

        self.client.post(
            'books/{}/add/{}/'.format(book_id, story_id), 
            data=form_data, 
            headers={
                "Referer": response.url
            },
            name="Authenticated Add Story to Book (/books/<book_id>/add/<story_id>)")
        if response.status_code != 200: return

        if story_id in self.private_stories:
            self.private_stories[story_id]["books"].append(book_id)
        else:
            with public_stories_lock:
                public_stories[story_id]["books"].append(book_id)

        self.private_books[book_id]["stories"].append(story_id)

    @task(6)
    def love_story(self):
        if (not self.signed_up): return
        public_stories_keys = [key for key, value in public_stories.items() if (value.get("user") != self.username and key not in self.liked_stories)]
        if (len(public_stories_keys) == 0): return
        story_id = random.choice(public_stories_keys)

        response = self.client.get('stories/{}/'.format(story_id), name="Authenticated Love Story (/stories/<story_id>)")
        if response.status_code != 200: return
        form_data = {
            "csrfmiddlewaretoken": self.get_csrf_token(response),
        }
        self.client.post(
            'stories/{}/love/'.format(story_id), 
            data=form_data, 
            headers={
                "Referer": response.url
            },
            name="Authenticated Love Story (/stories/<story_number>/love/)")
        self.liked_stories.append(story_id)

    @task(6)
    def follow_user(self):
        if (not self.signed_up): return
        users = [ x for x in all_users if x != self.username and x not in self.following]
        if len(users) == 0: return

        user_to_follow = random.choice(users)
        self.client.get('/users/{}/follow/'.format(user_to_follow), name="Follow User (/users/<user_number>/follow)")
        self.following.append(user_to_follow)

    @task(6)
    def unfollow_user(self):
        if (not self.signed_up): return
        if len(self.following) == 0: return

        user_to_unfollow = random.choice(self.following)
        self.client.get('/users/{}/unfollow/'.format(user_to_unfollow), name="Unfollow User (/users/<user_number>/unfollow)")
        self.following.remove(user_to_unfollow)

    @task(6)
    def comment_story(self):
        if (not self.signed_up): return
        accessible_stories = list(self.private_stories.keys())
        if len(accessible_stories) == 0: return
        story_id = random.choice(accessible_stories)

        response = self.client.get('stories/{}/history'.format(story_id), name="Authenticated story history (/stories/<story_id>/history)")
        if response.status_code != 200: return
        form_data = {
            "csrfmiddlewaretoken": self.get_csrf_token(response),
            "comment": "This is a test comment."
        }
        self.client.post(
            'stories/{}/history/'.format(story_id), 
            data=form_data, 
            headers={
                "Referer": response.url
            },
            name="Authenticated Comment Story (/stories/<story_id>/comment)")

    def on_stop(self):
        print("🔥 User {} has stopped running.".format(self.username))
        print("🔥 Printing all user stories into summary file...")
        with summary_file_lock:
            with open(summary_file, 'a') as summary:
                summary.write("\n################################################################\n")
                if (not self.signed_up): 
                    summary.write("Username: {} couldn't sign up ".format(self.username))
                    return
                summary.write("Username: {} Password: {}\n".format(self.username, self.password))
                summary.write("Public Stories \n")
                public_stories_keys = ["{} : {}".format(key, value.get("title")) 
                                       for key, value in public_stories.items() 
                                       if value.get("user") == self.username]
                summary.write(','.join(public_stories_keys))
                summary.write("\nPrivate Stories\n")
                private_stories_keys = ["{} : {}".format(key, value.get("title")) 
                                       for key, value in self.private_stories.items() 
                                    ]
                summary.write(','.join(private_stories_keys))