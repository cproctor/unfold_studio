
def unseen_events(request):
    if request.user.is_authenticated():
        return {"unseen_events": request.user.events.filter(seen=False).count()}
    else:
        return {"unseen_events": 0}
