from literacy_events.models import Notification
from prompts.models import Prompt

def notifications(request):
    if request.user.is_authenticated:
        unseen_events = Notification.objects.for_request(request).filter(seen=False).count()
        unsubmitted_prompts = Prompt.objects.unsubmitted_for_user(request.user).count()
        notifications = unseen_events + unsubmitted_prompts
        return {
            "unseen_events": unseen_events,
            "unsubmitted_prompts": unsubmitted_prompts,
            "notifications": notifications,
        }
    else:
        return {"unseen_events": 0}
