from app.serializers import ReactionSerializer
from app.services.notification_service import noti_reaction_add

def reaction(capsule,request):
    serializer = ReactionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(user=request.user,capsule=capsule)
    noti_reaction_add(request.user,capsule)