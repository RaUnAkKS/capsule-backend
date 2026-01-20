from app.models import Notification,Capsule,Collaboration

def noti_invite_accept(user,capsule):
    Notification.objects.update_or_create(user=capsule.creator,capsule=capsule,notification_type="INVITE_ACCEPTED",message=f"{user.username} accepted your invite",defaults={"is_sent":True})

def noti_invite_decline(user,capsule):
    Notification.objects.update_or_create(user=capsule.creator,capsule=capsule,notification_type="INVITE_DECLINE",message=f"{user.username} declined your invite",defaults={"is_sent":True})

def noti_reaction_add(requesting_user,capsule):
    users = set()

    users.add(capsule.creator)
    for collab in Collaboration.objects.filter(capsule=capsule):
        users.add(collab.user)
    users.discard(requesting_user)
    for user in users:
        Notification.objects.create(user=user,capsule=capsule,notification_type="REACTION",message=f"{requesting_user} is reacted on {capsule.title}")
    