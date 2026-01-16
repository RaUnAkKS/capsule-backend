from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)


class Capsule(models.Model):
    UNLOCK_CHOICES = [
        ('DATE','Date'),
        ('EVENT','Event'),
    ]
    PRIVACY_CHOICES = [
        ('PRIVATE','Private'),
        ('SHARED','Shared'),
        ('PUBLIC','Public'),
    ]
    creator = models.ForeignKey(User,on_delete=models.CASCADE,related_name="capsules")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    theme = models.CharField(max_length=100)
    unlock_type = models.CharField(max_length=20,choices=UNLOCK_CHOICES)
    unlock_date = models.DateTimeField(null=True,blank=True)
    is_unlocked = models.BooleanField(default=False)
    privacy_level = models.CharField(max_length=20,choices=PRIVACY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Memories(models.Model):
    MEMORY_CHOICES =[
        ('TEXT','Text'),
        ('IMAGE','Image'),
        ('VIDEO','Video'),
        ('AUDIO','Audio'),
    ]
    capsule = models.ForeignKey(Capsule,on_delete=models.CASCADE,related_name="memo_capsule")
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name="memories")
    memory_type = models.CharField(max_length=20,choices=MEMORY_CHOICES)
    text_content = models.TextField(null=True,blank=True)
    file = models.FileField(upload_to='memories/',null=True,blank=True)
    caption = models.CharField(max_length=100,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    
class Recipients(models.Model):
    ROLE_CHOICES = [
        ('VIEWER','Viewer'),
        ('CONTRIBUTOR','Contributor'),
    ]
    capsule = models.ForeignKey(Capsule,on_delete=models.CASCADE,related_name="reciep_capsule")
    email = models.EmailField()
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="reciep_user")
    role = models.CharField(max_length=20,choices=ROLE_CHOICES)
    has_accepted = models.BooleanField(default=False)
    decline = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)

class Collaboration(models.Model):
    PERMISSION_CHOICES = [
        ('OWNER','Owner'),
        ('CONTRIBUTOR','Contributor'),
        ('VIEWER','Viewer'),
    ]
    capsule = models.ForeignKey(Capsule,on_delete=models.CASCADE,related_name="collab_capsule")
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="collab_user")
    permission = models.CharField(max_length=20,choices=PERMISSION_CHOICES)
    added_at = models.DateTimeField(auto_now_add=True)

class UnlockEvent(models.Model):
    EVENT_CHOICES = [
        ('WEDDING','Wedding'),
        ('GRADUATION','Graduation'),
        ('OTHER','Others')
    ]
    capsule = models.ForeignKey(Capsule,on_delete=models.CASCADE,related_name="event_capsule")
    event_name = models.CharField(max_length=20,choices=EVENT_CHOICES)
    event_triggered = models.BooleanField(default=False)
    triggered_at = models.DateTimeField(null=True,blank=True)

class Notification(models.Model):
    NOTIFICATION_CHOICES = [
        ('UNLOCK','Unlock'),
        ('INVITE','Invite'),
        ('REMINDER','Reminder'),
        ('INVITE_ACCEPTED','Invite_accepted'),
        ('INVITE_DECLINE','Invite_decline'),
        ('REACTION','Reaction')
    ]
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="notification_user")
    capsule = models.ForeignKey(Capsule,on_delete=models.CASCADE,related_name="notification_capsule")
    notification_type = models.CharField(max_length=20,choices=NOTIFICATION_CHOICES)    
    message = models.TextField(null=True,blank=True)
    is_sent = models.BooleanField(default=False)
    is_seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Reaction(models.Model):
    capsule = models.ForeignKey(Capsule,on_delete=models.CASCADE,related_name="reaction_capsule")
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="reaction_user")
    commented_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
