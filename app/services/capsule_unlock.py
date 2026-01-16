from django.utils import timezone
from app.models import Capsule
from .notifications import notify_capsule_unlocked

def unlock_capsule(capsule:Capsule):
    if capsule.is_unlocked:
        return False
    capsule.is_unlocked = True
    capsule.updated_at = timezone.now()
    capsule.save(update_fields=["is_unlocked","updated_at"])
    notify_capsule_unlocked(capsule)
    return True