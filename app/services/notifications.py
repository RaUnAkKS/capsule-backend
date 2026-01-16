from app.models import Notification, Collaboration, Recipients

def notify_capsule_unlocked(capsule):
    users = set()

    for collab in Collaboration.objects.filter(capsule=capsule):
        users.add(collab.user)

    for reci in Recipients.objects.filter(capsule=capsule,has_accepted=True):
        users.add(reci.user)

    for user in users : 
        Notification.objects.create(user=user,capsule=capsule,notification_type="UNLOCK",message=f"Capsule '{capsule.title}' has been unlocked 🎉")

