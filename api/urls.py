from app.views import *
from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView,)

urlpatterns = [
    path('register/',RegisterAPIView.as_view(),name='register'),

    path('capsules/',CapsuleCreateAPIView.as_view(),name='capsule-create'),
    path('capsules/list/',CapsuleListAPIView.as_view(),name='capsule-list'),
    path('capsules/<int:capsule_id>/',CapsuleDetailAPIView.as_view(),name='capsule-detail'),

    path('capsules/<int:capsule_id>/memories/',MemoryListAPIView.as_view(),name='memory-list'),
    path('capsules/<int:capsule_id>/memories/add/',MemoryCreateAPIView.as_view(),name='memory-create'),
    path('capsules/<int:capsule_id>/memories/<int:memory_id>/',MemoryDetailAPIView.as_view(),name='memory-detail'),

    path('capsules/<int:capsule_id>/recipients/add/',RecipientCreateAPIView.as_view(),name='recipient-add'),
    path('capsules/<int:capsule_id>/collaborators/',CollaborationListAPIView.as_view(),name='collaborator-list'),
    path('capsules/<int:capsule_id>/recipients/',RecipientListAPIView.as_view(),name='recipient-list'),
    path('capsules/<int:capsule_id>/unlock/',CapsuleEventUnlockAPIView.as_view(),name='capsule-event-unlock'),

    path('capsules/invites/',InviteListAPIView.as_view(),name='invite-list'),
    path('capsules/<int:capsule_id>/invites/accept/',InviteAcceptAPIView.as_view(),name='invite-accept'),
    path('capsules/<int:capsule_id>/invites/decline/',InviteDeclineAPIView.as_view(),name='invite-decline'),
    path('capsules/<int:capsule_id>/reactions/',ReactionsAPIView.as_view(),name='reaction-add'),

    path('notifications/',NotificationListAPIView.as_view(),name='notification-list'),
    path('notifications/<int:id>/read/',NotificationMarkAPIView.as_view(),name='mark_read'),
    path('notifications/read-all/',NotificationMarkAllAPIView.as_view(),name='mark-all-read'),
    path('notifications/unread-count/',NotificationsUnreadAPIView.as_view(),name='noti-count'),
    path('capsules/<int:capsule_id>/countdown',CountdownTimerAPIView.as_view(),name='countdown'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


]