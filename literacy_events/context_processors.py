from literacy_events.models import Notification

def unseen_events(request):
    if request.user.is_authenticated:
        return {"unseen_events": Notification.objects.for_request(request).filter(seen=False).count()}
    else:
        return {"unseen_events": 0}
