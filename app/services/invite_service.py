from app.models import Recipients,Collaboration
from app.services.notification_service import noti_invite_accept,noti_invite_decline

def accept_invite(recipient,capsule,user):
    recipient.has_accepted=True
    recipient.save(update_fields=["has_accepted"])

    Collaboration.objects.update_or_create(capsule=capsule,user=user,defaults={"permission":recipient.role})

    noti_invite_accept(user,capsule)

def decline_invite(recipient,capsule,user):
    recipient.decline=True
    recipient.save(update_fields=["decline"])
    noti_invite_decline(user,capsule)