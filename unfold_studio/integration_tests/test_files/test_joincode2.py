from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from literacy_groups.models import LiteracyGroup, JoinCode
from literacy_events.models import LiteracyEvent
from django.contrib.sites.models import Site
from profiles.models import Profile
from django.test import override_settings

@override_settings(ROOT_URLCONF='unfold_studio.urls.base')
class LiteracyGroupLeaveTest(TestCase):
    def setUp(self):
        # 1. Create the Site
        self.site = Site.objects.get_current()
        self.site.domain = 'testserver'
        self.site.name = 'testserver'
        self.site.save()

        # 2. Create the Teacher
        self.teacher = User.objects.create_user(username='teacher_chris', password='password123')
        teacher_profile, _ = Profile.objects.get_or_create(user=self.teacher)
        teacher_profile.is_teacher = True
        teacher_profile.save()

        # 3. Create the Student
        self.student = User.objects.create_user(username='student_aria', password='password123')

        # 4. Create the Group
        self.group = LiteracyGroup.objects.create(name="Group B", site=self.site)
        self.group.leaders.add(self.teacher)
        self.group.members.add(self.teacher)

        # 5. Pre-create a join code and assign the student directly
        #    (simulates a student who already joined via the join workflow)
        self.join_code = JoinCode.objects.create(
            group=self.group,
            code=self.group.new_join_code(),
            assigned_user=self.student
        )
        self.group.members.add(self.student)

        # 6. Pre-create the join event to reflect their prior join
        LiteracyEvent.objects.create(
            event_type=LiteracyEvent.JOINED_LITERACY_GROUP,
            subject=self.student,
            literacy_group=self.group,
        )

    # ── HAPPY PATH ─────────────────────────────────────────────────────────────

    def test_student_can_leave_group(self):
        """A student who joined can successfully leave the group."""
        self.client.login(username='student_aria', password='password123')

        leave_url = reverse('leave_group', kwargs={'pk': self.group.pk})
        response = self.client.post(leave_url, follow=True)

        print(f"\nRedirect chain: {response.redirect_chain}")
        print(f"Status: {response.status_code}")

        self.assertEqual(response.status_code, 200)

        # 1. Student is no longer a member
        self.assertNotIn(self.student, self.group.members.all())

        # 2. The join code was freed (assigned_user cleared)
        self.join_code.refresh_from_db()
        self.assertIsNone(self.join_code.assigned_user)

        # 3. A Leave event was created
        event_exists = LiteracyEvent.objects.filter(
            subject=self.student,
            literacy_group=self.group,
            event_type=LiteracyEvent.LEFT_LITERACY_GROUP
        ).exists()
        self.assertTrue(event_exists)

        print(f"\n Success: {self.student.username} left {self.group.name}")

    # ── EDGE CASES ─────────────────────────────────────────────────────────────

    def test_teacher_cannot_leave_group_they_lead(self):
        """A teacher who is a leader should be blocked from leaving."""
        self.client.login(username='teacher_chris', password='password123')

        leave_url = reverse('leave_group', kwargs={'pk': self.group.pk})
        response = self.client.post(leave_url, follow=True)

        # Teacher should still be a member
        self.assertIn(self.teacher, self.group.members.all())

        print(f"\n Success: teacher correctly blocked from leaving their own group")


    def test_used_code_is_freed_when_student_leaves(self):
        """Leaving the group clears the assigned_user on the join code."""
        self.client.login(username='student_aria', password='password123')

        leave_url = reverse('leave_group', kwargs={'pk': self.group.pk})
        self.client.post(leave_url, follow=True)

        self.join_code.refresh_from_db()
        self.assertIsNone(self.join_code.assigned_user)

        print(f"\n Success: join code {self.join_code.code} was freed after student left")