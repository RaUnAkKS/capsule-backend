from .models import *
from rest_framework import serializers

class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email']

class UserRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=200)
    password = serializers.CharField(write_only=True)

    def validate(self,data):
        username = data.get('username')
        email = data.get('email')
        if username:
            if User.objects.filter(username=username).exists():
                raise serializers.ValidationError('username already taken')
        if email:
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError('email already registered')
        return data
    
    def create(self,validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    
class CapsuleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Capsule
        exclude = ['creator','is_unlocked','created_at']

    def validate(self, data):
        unlock_type = data.get('unlock_type')
        unlock_date = data.get('unlock_date')

        if unlock_type == 'DATE' and not unlock_date:
            raise serializers.ValidationError('unlock_date is required for DATE unlock')

        if unlock_type == 'EVENT' and unlock_date:
            raise serializers.ValidationError('unlock_date must be null for EVENT unlock')

        return data
    
class CapsuleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Capsule
        fields = ['id','title','theme','is_unlocked','unlock_type','unlock_date','created_at']

class CapsuleDetailSerializer(serializers.ModelSerializer):
    creator = UserPublicSerializer()
    user_role = serializers.SerializerMethodField()

    class Meta:
        model = Capsule
        fields = ['id','title','description','theme','creator','unlock_type','unlock_date','is_unlocked','privacy_level','created_at', 'user_role']

    def get_user_role(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                collab = Collaboration.objects.filter(capsule=obj, user=request.user).first()
                if collab:
                    return collab.permission
            except Exception:
                pass
            
            if obj.creator == request.user:
                return 'OWNER'
        return None

class MemoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Memories
        fields = ['memory_type','text_content','caption','file']

    def validate(self,data):
        memory_type = data.get('memory_type')
        text_content = data.get('text_content')

        if memory_type=='TEXT' and not text_content:
            raise serializers.ValidationError('text_content is required for TEXT memory')
        if memory_type!='TEXT' and text_content:
            raise serializers.ValidationError('text_content should be empty for media memory')
        return data
class MemoryListSerializer(serializers.ModelSerializer):
    created_by = UserPublicSerializer()
    class Meta:
        model = Memories
        fields = ['id','memory_type','caption','created_at','created_by']

class MemoryDetailSerializer(serializers.ModelSerializer):
    created_by = UserPublicSerializer()
    class Meta:
        model = Memories
        fields = ['id','memory_type','text_content','caption','created_by','created_at','file']

class RecipientCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    user = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = Recipients
        fields = ['role','user','username']

    def validate(self,data):
        username = data.get('username')
        capsule = self.context.get('capsule')
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError('user does not exist')
            
        if user == capsule.creator:
            raise serializers.ValidationError('user cannot be invited')
        
        if Recipients.objects.filter(capsule=capsule, user=user).exists():
            raise serializers.ValidationError('user already invited')
            
        data['user'] = user
        return data

    def create(self, validated_data):
        user = validated_data.pop('user')
        username = validated_data.pop('username')
        recipient = Recipients.objects.create(
            user=user,
            email=user.email,
            **validated_data
        )
        return recipient
        
class RecipientListSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    class Meta:
        model = Recipients
        fields = ['email','role','has_accepted','user','decline']
    

class CollaborationSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    class Meta:
        model = Collaboration
        fields = ['permission','added_at','user']

    
class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = ['id','notification_type','message','created_at','is_sent','is_seen','capsule']


class ReactionSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = Reaction
        fields = ['id', 'capsule', 'user', 'commented_text', 'created_at']
        read_only_fields = ['id', 'capsule', 'user', 'created_at']