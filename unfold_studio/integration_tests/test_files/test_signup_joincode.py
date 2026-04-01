from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from literacy_groups.models import LiteracyGroup, JoinCode
from django.contrib.sites.models import Site
from profiles.models import Profile
from django.conf import settings
from django.test import override_settings


@override_settings(ROOT_URLCONF='unfold_studio.urls.base')
class SignupJoinCodeWorkflowTest(TestCase):
    def setUp(self):
       # 1. Create the Site
        self.site = Site.objects.get_current()
        self.site.domain = 'testserver'
        self.site.name = 'testserver'
        self.site.save()

        # 2. Create the Teacher User
        self.teacher = User.objects.create_user(username='teacher_chris', password='password123')

        # 3. Give them the "Teacher Pass"
        # Since you likely have a signal creating profiles, we use get_or_create
        teacher_profile, _ = Profile.objects.get_or_create(user=self.teacher)
        teacher_profile.is_teacher = True
        teacher_profile.save()

        # 4. Create a Group and assign the teacher as leader
        self.group = LiteracyGroup.objects.create(name="Group B", site=self.site)

        self.group.leaders.add(self.teacher)
        self.group.members.add(self.teacher)

    def test_full_signup_and_join_process(self):
        """Tests that a teacher can generate a code and a student can sign up using it."""
        self.client.login(username='teacher_chris', password='password123')

        gen_url = reverse('generate_codes', kwargs={'pk': self.group.pk})
        print(f"\nGenerated URL: {gen_url}")
        print(f"Group PK: {self.group.pk}")

        # Generate 1 code
        response = self.client.post(gen_url, {'quantity': 1}, follow=True)

        # NOW we can print response info
        print("Final URL:", response.wsgi_request.path)
        print("Redirect chain:", response.redirect_chain)
        print("Status:", response.status_code)

        self.assertEqual(response.status_code, 200)

        # Grab one of the codes to use
        test_code_obj = JoinCode.objects.filter(group=self.group).first()
        test_code_str = test_code_obj.code

        # --- PHASE 2: STUDENT SIGNS UP WITH JOIN CODE ---
        self.client.logout()

        join_signup_url = reverse('join_student')
        response = self.client.post(join_signup_url, {
            'user_type': 'student',
            'join_code': test_code_str,
            'username': 'student_aria',
            'password1': 'password12345',
            'password2': 'password12345',
        }, follow=True)

        print("Student signup final URL:", response.wsgi_request.path)
        print("Student signup redirect chain:", response.redirect_chain)
        print("Student signup status:", response.status_code)

        # --- PHASE 3: VERIFICATION ---
        # 1. Check that the student user was created
        self.assertTrue(User.objects.filter(username='student_aria').exists())
        student = User.objects.get(username='student_aria')

        # 2. Check if the code now belongs to the student
        test_code_obj.refresh_from_db()
        self.assertEqual(test_code_obj.assigned_user, student)

        # 3. Check if the student is officially a member of the group
        self.assertIn(student, self.group.members.all())

        print(f"\n Success: {student.username} signed up and joined {self.group.name} using code {test_code_str}")

    def test_regular_user_signup(self):
        """Tests that a regular user can sign up through the normal signup page."""
        signup_url = reverse('signup')
        response = self.client.post(signup_url, {
            'user_type': 'regular',
            'username': 'regular_user_1',
            'email': 'regular_user_1@example.com',
            'password1': 'password12345',
            'password2': 'password12345',
        }, follow=True)

        print("\nRegular signup final URL:", response.wsgi_request.path)
        print("Regular signup redirect chain:", response.redirect_chain)
        print("Regular signup status:", response.status_code)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='regular_user_1').exists())

        print("\n Success: regular_user_1 signed up successfully")
