from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, UserProfile, Post, Comment, Like, Follow
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture', 'bio', 'website', 'location']

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    profile_picture = serializers.ImageField(source='user.profile_picture', read_only=True)
    bio = serializers.CharField(source='user.bio', read_only=True)
    website = serializers.URLField(source='user.website', read_only=True)
    location = serializers.CharField(source='user.location', read_only=True)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'profile_picture', 'bio', 'website', 'location', 'followers_count', 'following_count', 'created_at']
    
    def get_followers_count(self, obj):
        return obj.followers.count()
    
    def get_following_count(self, obj):
        return obj.user.following.count()

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                else:
                    raise serializers.ValidationError('User account is disabled.')
            else:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
        else:
            raise serializers.ValidationError('Must include username and password.')
        
        return data

class CommentSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)  
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at']
        read_only_fields = ['user', 'created_at']

class PostSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)  
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'user', 'content', 'image', 'created_at', 'likes_count', 'comments_count', 'comments']
        read_only_fields = ['user', 'created_at']
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_comments_count(self, obj):
        return obj.comments.count()

class LikeSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)  
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']

class FollowSerializer(serializers.ModelSerializer):
    follower = UserSimpleSerializer(read_only=True)  
    following = UserSimpleSerializer(read_only=True)  
    
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['follower', 'created_at']


class UserSearchSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.CharField(source='user.email')
    bio = serializers.CharField(source='user.bio')
    profile_picture = serializers.ImageField(source='user.profile_picture')
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'bio', 'profile_picture', 'followers_count', 'following_count', 'is_following']
    
    def get_followers_count(self, obj):
        return obj.followers_count
    
    def get_following_count(self, obj):
        return obj.following_count
    
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(
                follower=request.user, 
                following=obj.user
            ).exists()
        return False
    

class FollowUserView(APIView):
    def post(self, request, user_id):
        user_to_follow = get_object_or_404(User, id=user_id)
        follow, created = Follow.objects.get_or_create(
            follower=request.user, 
            following=user_to_follow
        )
        
        if created:
            return Response({'message': f'Now following {user_to_follow.username}'})
        return Response({'message': f'Already following {user_to_follow.username}'})
    
    def delete(self, request, user_id):
        user_to_unfollow = get_object_or_404(User, id=user_id)
        Follow.objects.filter(
            follower=request.user, 
            following=user_to_unfollow
        ).delete()
        return Response({'message': f'Unfollowed {user_to_unfollow.username}'})