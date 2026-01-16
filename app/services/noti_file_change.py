from app.models import Notification
from django.shortcuts import get_object_or_404


def mark_read(user,id):
    noti = get_object_or_404(Notification,user=user,id=id)
    if not noti.is_seen:
        noti.is_seen=True
        noti.save(update_fields=['is_seen'])

def mark_all_read(user):
    notifications = Notification.objects.filter(user=user,is_seen=False).update(is_seen=True)