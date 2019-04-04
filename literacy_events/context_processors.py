from literacy_events.models import Notification

def unseen_events(request):
    if request.user.is_authenticated:
        return {"unseen_events": Notification.objects.for_user(request.user).filter(seen=False).count()}
    else:
        return {"unseen_events": 0}
