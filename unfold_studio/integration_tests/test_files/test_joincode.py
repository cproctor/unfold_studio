from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from literacy_groups.models import LiteracyGroup, JoinCode
from literacy_events.models import LiteracyEvent
from django.contrib.sites.models import Site
from profiles.models import Profile
from django.conf import settings
from django.test import override_settings

@override_settings(ROOT_URLCONF='unfold_studio.urls.base')
class LiteracyGroupWorkflowTest(TestCase):
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

        # 2. Create a Student
        self.student = User.objects.create_user(username='student_aria', password='password123')

        # 3. Create a Group and assign the teacher as leader
        self.group = LiteracyGroup.objects.create(name="Group B",site=self.site)

        self.group.leaders.add(self.teacher)
        self.group.members.add(self.teacher)

    def test_full_invite_and_join_process(self):
        """Tests that a teacher can generate a code and a student can use it to join."""
        self.client.login(username='teacher_chris', password='password123')
    
        gen_url = reverse('generate_codes', kwargs={'pk': self.group.pk})
        print(f"\nGenerated URL: {gen_url}")
        print(f"Group PK: {self.group.pk}")

        # Generate 2 codes
        response = self.client.post(gen_url, {'quantity': 2}, follow=True)
    
        # NOW we can print response info
        print("Final URL:", response.wsgi_request.path)
        print("Redirect chain:", response.redirect_chain)
        print("Status:", response.status_code)

        self.assertEqual(response.status_code, 200)

       # self.assertEqual(JoinCode.objects.filter(group=self.group).count(), 2)
       
        # Grab one of the codes to use
        test_code_obj = JoinCode.objects.filter(group=self.group).first()
        test_code_str = test_code_obj.code
        
        # --- PHASE 2: STUDENT JOINS GROUP ---
        self.client.logout()
        self.client.login(username='student_aria', password='password123')
        
        # Target the JoinGroupView with the code in the URL params
        join_url = reverse('join_group', kwargs={'pk': self.group.pk})
        response = self.client.get(f"{join_url}?code={test_code_str}", follow=True)

        # --- PHASE 3: VERIFICATION ---
        # 1. Check if the code now belongs to the student (The "Student 1" replacement logic)
        test_code_obj.refresh_from_db()
        self.assertEqual(test_code_obj.assigned_user, self.student)

        # 2. Check if the student is officially a member of the group
        self.assertIn(self.student, self.group.members.all())

        # 3. Check if a Join Event was created in the database
        event_exists = LiteracyEvent.objects.filter(
            subject=self.student, 
            literacy_group=self.group,
            event_type=LiteracyEvent.JOINED_LITERACY_GROUP
        ).exists()
        self.assertTrue(event_exists)

        print(f"\n Success: {self.student.username} joined {self.group.name} using code {test_code_str}")
