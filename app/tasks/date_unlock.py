from django.utils import timezone
from app.models import Capsule
from app.services.capsule_unlock import unlock_capsule

def unlock_due_capsules():
    time = timezone.now()
    capsules = Capsule.objects.filter(unlock_type="DATE",is_unlocked=False,unlock_date__lte=time)
    for capsule in capsules:
        unlock_capsule(capsule)