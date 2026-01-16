from rest_framework.permissions import BasePermission
from .models import *

def get_user_permission(user,capsule):
    try:
        collab = Collaboration.objects.get(user=user,capsule=capsule)
        return collab.permission
    except Collaboration.DoesNotExist:
        return None
    
def safe_get_capsule(view):
    try:
        return view.get_capsule()
    except Exception:
        return None
    
class IsCapsuleOwner(BasePermission):
    def has_permission(self,request,view):
        capsule = safe_get_capsule(view)

        if not capsule:
            return False
        return (request.user.is_authenticated and 
                get_user_permission(request.user,capsule)=='OWNER')
    
class CanAddMemory(BasePermission):
    def has_permission(self,request,view):
        capsule = safe_get_capsule(view)

        if not capsule:
            return False
        permission = get_user_permission(request.user,capsule)
        return(request.user.is_authenticated and not capsule.is_unlocked and(
               permission=='OWNER' or
                permission=='CONTRIBUTOR'))
    
class CanViewCapsule(BasePermission):
    def has_permission(self,request,view):
        capsule = safe_get_capsule(view)

        if not capsule:
            return False
        permission = get_user_permission(request.user,capsule)
        if capsule.is_unlocked:
            return (request.user.is_authenticated and
                    (permission=='OWNER' or permission=='CONTRIBUTOR' or permission=='VIEWER'))
        else:
            return (request.user.is_authenticated and
                    (permission=='OWNER' or permission=='CONTRIBUTOR'))
        
class CanReact(BasePermission):
    def has_permission(self, request, view):
        capsule = safe_get_capsule(view)

        if not capsule:
            return False
        permission = get_user_permission(request.user,capsule)
        return (request.user.is_authenticated and capsule.is_unlocked and permission is not None)