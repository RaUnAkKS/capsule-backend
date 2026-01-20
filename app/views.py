from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Capsule, Collaboration
from .serializers import *
from .permissions import *
from app.services.capsule_unlock import unlock_capsule
from app.tasks.date_unlock import unlock_due_capsules
from app.services.invite_service import accept_invite,decline_invite
from app.services.reaction_add import reaction
from rest_framework.pagination import PageNumberPagination
from .pagination import CapsulePagination,MemoryCursorPagination
from app.services.noti_file_change import mark_read,mark_all_read
from datetime import timedelta
from rest_framework.parsers import MultiPartParser, FormParser


class RegisterAPIView(APIView):
    permission_classes = []

    def post(self,request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message":"User registered Successfully"},status=status.HTTP_201_CREATED)
    

class CapsuleCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        serializer = CapsuleCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        capsule = serializer.save(creator=request.user)

        Collaboration.objects.create(capsule=capsule,user=request.user,permission='OWNER')
        return Response({"message":"Capsule created succesfully"},status=status.HTTP_201_CREATED)

class CapsuleListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        search_term = request.query_params.get('search',None)
        if search_term == 'Locked':
            capsules = Capsule.objects.filter(collab_capsule__user=request.user,is_unlocked=False).distinct().order_by("-created_at")
        elif search_term == 'Unlocked':
            capsules = Capsule.objects.filter(collab_capsule__user=request.user,is_unlocked=True).distinct().order_by("-created_at")
        else:
            capsules = Capsule.objects.filter(collab_capsule__user=request.user).distinct().order_by("-created_at")
        
        paginator = PageNumberPagination()
        # Ensure we use the page size from settings if not overridden
        # paginator.page_size = 5 # Optional if you want to hardcode
        
        result_page = paginator.paginate_queryset(capsules, request)
        serializer = CapsuleListSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
class CapsuleDetailAPIView(APIView):
    permission_classes = [IsAuthenticated,CanViewCapsule]
    
    def get_capsule(self):
        return get_object_or_404(Capsule,id=self.kwargs['capsule_id'])
    
    def get(self,request,capsule_id):
        unlock_due_capsules()
        capsule = self.get_capsule()
        serializer = CapsuleDetailSerializer(capsule, context={'request':request})
        return Response(serializer.data)
    
class MemoryCreateAPIView(APIView):
    permission_classes = [IsAuthenticated,CanAddMemory]
    parser_classes = [MultiPartParser, FormParser]

    def get_capsule(self):
        return get_object_or_404(Capsule,id=self.kwargs['capsule_id'])
    
    def post(self,request,capsule_id):
        capsule = self.get_capsule()
        serializer = MemoryCreateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(capsule=capsule,created_by=request.user)
        return Response({"message":"Memory added Succesfully"},status=status.HTTP_201_CREATED)

class MemoryListAPIView(APIView):
    permission_classes = [IsAuthenticated,CanViewCapsule]

    def get_capsule(self):
        return get_object_or_404(Capsule,id=self.kwargs['capsule_id'])
    
    def get(self,request,capsule_id):
        capsule = self.get_capsule()
        
        # Security check: If locked and user is VIEWER, return empty list
        permission = get_user_permission(request.user, capsule)
        if not capsule.is_unlocked and permission == 'VIEWER':
             return Response({'count': 0, 'next': None, 'previous': None, 'results': []})

        memories = capsule.memo_capsule.order_by('-created_at')
        
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(memories, request)
        serializer = MemoryListSerializer(result_page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    
class MemoryDetailAPIView(APIView):

    permission_classes = [IsAuthenticated,CanViewCapsule]
    def get_capsule(self):
        return get_object_or_404(Capsule,id=self.kwargs['capsule_id'])

    def get(self,request,capsule_id,memory_id):
        capsule = self.get_capsule()
        
        # Security check: specific memory access should also be blocked
        permission = get_user_permission(request.user, capsule)
        if not capsule.is_unlocked and permission == 'VIEWER':
             return Response({"detail": "Capsule is locked"}, status=status.HTTP_403_FORBIDDEN)
        memory = get_object_or_404(capsule.memo_capsule, id=memory_id)
        serializer = MemoryDetailSerializer(memory, context={'request': request})
        return Response(serializer.data)

class MemoryAllDetailAPIView(APIView):
    
    permission_classes=[IsAuthenticated,CanViewCapsule]
    def get_capsule(self):
        return get_object_or_404(Capsule,id=self.kwargs['capsule_id'])
    
    def get(self,request,capsule_id):
        capsule = self.get_capsule()
        permission = get_user_permission(request.user, capsule)
        if not capsule.is_unlocked and permission == 'VIEWER':
             return Response({"detail": "Capsule is locked"}, status=status.HTTP_403_FORBIDDEN)
        search_term = request.query_params.get('search',None)
        if search_term:
            memory = capsule.memo_capsule.filter(created_by__username__icontains=search_term).order_by('-created_at')
        else:
            memory = capsule.memo_capsule.all().order_by('-created_at')
        paginator = MemoryCursorPagination()
        result_page = paginator.paginate_queryset(memory,request)
        serializer = MemoryDetailSerializer(result_page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

class RecipientCreateAPIView(APIView):
    permission_classes = [IsAuthenticated,IsCapsuleOwner]
    def get_capsule(self):
        return get_object_or_404(Capsule,id=self.kwargs['capsule_id'])
    
    def post(self,request,capsule_id):
        
        capsule = self.get_capsule()
        if capsule.privacy_level == 'PRIVATE':
            return Response({"detail":"You can't invite recipient to private capsule"},status=status.HTTP_400_BAD_REQUEST)
        serializer = RecipientCreateSerializer(data=request.data,context={'capsule':capsule})
        if serializer.is_valid(raise_exception=True):
            serializer.save(capsule=capsule)
            Notification.objects.create(
                capsule = capsule,
                user = serializer.validated_data['user'],
                notification_type = 'INVITE',
                message = f"You have been invited to {serializer.validated_data['role']} the capsule {capsule.title} by {capsule.creator.username}"
            )

        return Response({"message":"Recipient invited"},status=status.HTTP_201_CREATED) 

class RecipientListAPIView(APIView):
    permission_classes = [IsAuthenticated,CanViewCapsule]
    def get_capsule(self):
        return get_object_or_404(Capsule,id=self.kwargs['capsule_id'])
    def get(self,request,capsule_id):
        capsule = self.get_capsule()
        recipients = capsule.reciep_capsule.filter(has_accepted=False).order_by('added_at')
        serializer = RecipientListSerializer(recipients,many=True)
        return Response(serializer.data)
    
class CollaborationListAPIView(APIView):
    permission_classes = [IsAuthenticated,CanViewCapsule]
    def get_capsule(self):
        return get_object_or_404(Capsule,id=self.kwargs['capsule_id'])
    def get(self,request,capsule_id):
        capsule = self.get_capsule()
        collaborators = capsule.collab_capsule.all()
        serializer = CollaborationSerializer(collaborators,many=True)
        return Response(serializer.data)

class CapsuleEventUnlockAPIView(APIView):
    permission_classes = [IsAuthenticated,IsCapsuleOwner]

    def get_capsule(self):
        return get_object_or_404(Capsule,id=self.kwargs['capsule_id'])
    
    def post(self,request,capsule_id):
        capsule = self.get_capsule()

        if capsule.unlock_type!="EVENT":
            return Response({"error":"capsule is not event based"},status=status.HTTP_400_BAD_REQUEST)
        
        UnlockEvent.objects.update_or_create(capsule=capsule,defaults={"event_triggered": True,"triggered_at": timezone.now()})

        unlock_capsule(capsule)

        return Response({"message":"capsule unlocked successfully"},status=status.HTTP_200_OK)

class InviteListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        user=request.user
        invites = Notification.objects.filter(user=user,notification_type="INVITE",is_seen=False).order_by('-created_at')
        pagination = MemoryCursorPagination()
        result_page = pagination.paginate_queryset(invites,request)
        serializer = NotificationSerializer(result_page,many=True)
        return pagination.get_paginated_response(serializer.data)

class InviteAcceptAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_capsule(self):
        return get_object_or_404(Capsule,id=self.kwargs['capsule_id'])
    
    def post(self,request,capsule_id):
        capsule = self.get_capsule()
        recipient = get_object_or_404(Recipients,capsule=capsule,user=request.user)
        
        # Try to find notification and mark seen, but don't fail acceptance if missing
        notification = Notification.objects.filter(user=request.user,notification_type="INVITE",capsule=capsule).first()
        if notification:
            notification.is_seen=True
            notification.save(update_fields=["is_seen"])
            
        if recipient.has_accepted==True:
            # If already accepted, just return success (idempotent) or standard message
            return Response({"message":"Invite already accepted"},status=status.HTTP_200_OK)
            
        user = request.user
        accept_invite(recipient,capsule,user)

        return Response({"message":"Invite accepted successfully"},status=status.HTTP_200_OK)

class InviteDeclineAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get_capsule(self):
        return get_object_or_404(Capsule,id=self.kwargs['capsule_id'])
    def post(self,request,capsule_id):
        capsule = self.get_capsule()
        recipient = get_object_or_404(Recipients,capsule=capsule,user=request.user)
        
        notification = Notification.objects.filter(user=request.user,notification_type="INVITE",capsule=capsule).first()
        if notification:
            notification.is_seen=True
            notification.save(update_fields=["is_seen"])
            
        if recipient.has_accepted==True:
             return Response({"message":"Cannot decline, already accepted"},status=status.HTTP_400_BAD_REQUEST)
             
        user = request.user
        decline_invite(recipient,capsule,user)

        return Response({"message":"Invite declined successfully"},status=status.HTTP_200_OK)
    
class ReactionsAPIView(APIView):
    permission_classes = [IsAuthenticated,CanReact]

    def get_capsule(self):
        return get_object_or_404(Capsule,id=self.kwargs['capsule_id'])
    
    def post(self,request,capsule_id):
        capsule = self.get_capsule()
        reaction(capsule,request)
        
        return Response({"message":"Reaction is added successfully"},status=status.HTTP_200_OK)
    
    def get(self,request,capsule_id):
        capsule=self.get_capsule()
        
        # Security check: If locked and user is VIEWER, return empty list
        permission = get_user_permission(request.user, capsule)
        if not capsule.is_unlocked and permission == 'VIEWER':
             return Response({'count': 0, 'next': None, 'previous': None, 'results': []})

        reactions = Reaction.objects.filter(capsule=capsule).order_by('-created_at')
        
        # paginator = PageNumberPagination()
        # paginator.page_size = 5   # number of items per page
        # page = paginator.paginate_queryset(capsules, request)
        # serializer = CapsuleSerializer(page, many=True)
        # return paginator.get_paginated_response(serializer.data)
        # agar specific apiview mei pagination use karna hai bina folder banaye then use this

        # paginator = CapsulePagination()
        # page = paginator.paginate_queryset(capsules, request)
        # serializer = CapsuleSerializer(page, many=True)
        # return paginator.get_paginated_response(serializer.data)
        # agar folder bana ke karo then aise karte hai

        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(reactions, request)
        serializer = ReactionSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
class NotificationListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        user = request.user
        search_term = request.query_params.get('search',None)
        if search_term == 'Unread':
            noti = Notification.objects.filter(user=user,is_seen=False).order_by('-created_at')
        elif search_term == 'Read':
            noti = Notification.objects.filter(user=user,is_seen=True).order_by('-created_at')
        else:
            noti = Notification.objects.filter(user=user).order_by('-created_at')
        paginator = MemoryCursorPagination()
        result_page = paginator.paginate_queryset(noti,request)
        serializer = NotificationSerializer(result_page,many=True)
        return paginator.get_paginated_response(serializer.data)

class NotificationMarkAPIView(APIView):
    permission_classes=[IsAuthenticated]

    def post(self,request,id):
        user=request.user
        mark_read(user,id)
        return Response({"message":"notification is seen"},status=status.HTTP_200_OK)
    
class NotificationMarkAllAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        user = request.user
        mark_all_read(user)
        return Response({"message":"all notification is seen"},status=status.HTTP_200_OK)

class NotificationsUnreadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        noti_count = Notification.objects.filter(user=request.user,is_seen=False).count()
        return Response({"count":noti_count},status=status.HTTP_200_OK)
    


class CountdownTimerAPIView(APIView):
    permission_classes = [IsAuthenticated, CanViewCapsule]

    def get_capsule(self):
        return get_object_or_404(Capsule, id=self.kwargs['capsule_id'])

    def get(self, request, capsule_id):
        capsule = self.get_capsule()
        now = timezone.now()

        response = {
            "unlock_type": capsule.unlock_type,
            "is_unlocked": capsule.is_unlocked,
            "unlock_date": capsule.unlock_date,
            "server_time": now,
            "countdown_applicable": False,
            "seconds_remaining": 0,
        }

        if (
            capsule.unlock_type == "DATE"
            and not capsule.is_unlocked
            and capsule.unlock_date
            and capsule.unlock_date > now
        ):
            remaining = capsule.unlock_date - now

            response["countdown_applicable"] = True
            response["seconds_remaining"] = int(remaining.total_seconds())

        return Response(response, status=status.HTTP_200_OK)
