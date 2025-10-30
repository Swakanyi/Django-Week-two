from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.contrib.auth import login 
from django.contrib.auth import logout as auth_logout
from .models import User, UserProfile, Post, Comment, Like, Follow
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    PostSerializer, CommentSerializer, LikeSerializer, FollowSerializer, UserSearchSerializer
)
from django.shortcuts import render, redirect, get_object_or_404

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        
        return Response({
            'message': 'Use POST request with JSON data',
            'example': {
                'username': 'your_username', 
                'password': 'your_password'
            }
        })
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            return Response({
                'message': 'Login successful',
                'user_id': user.id,
                'username': user.username
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful'})


class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def update(self, request, *args, **kwargs):
        user = request.user
        user.bio = request.data.get('bio', user.bio)
        user.location = request.data.get('location', user.location)
        user.website = request.data.get('website', user.website)
        user.save()
        
        return Response({
            'message': 'Profile updated successfully',
            'bio': user.bio,
            'location': user.location,
            'website': user.website
        })

class UserProfileDetailView(generics.RetrieveAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return Post.objects.all().order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return Comment.objects.filter(post_id=post_id)
    
    def perform_create(self, serializer):
        post_id = self.kwargs['post_id']
        serializer.save(user=self.request.user, post_id=post_id)


class LikePostView(APIView):
    def post(self, request, post_id):
        post = generics.get_object_or_404(Post, id=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        
        if created:
            return Response({'message': 'Post liked'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Post already liked'}, status=status.HTTP_200_OK)
    
    def delete(self, request, post_id):
        post = generics.get_object_or_404(Post, id=post_id)
        Like.objects.filter(user=request.user, post=post).delete()
        return Response({'message': 'Post unliked'})

class LikeCommentView(APIView):
    def post(self, request, comment_id):
        comment = generics.get_object_or_404(Comment, id=comment_id)
        like, created = Like.objects.get_or_create(user=request.user, comment=comment)
        
        if created:
            return Response({'message': 'Comment liked'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Comment already liked'}, status=status.HTTP_200_OK)
    
    def delete(self, request, comment_id):
        comment = generics.get_object_or_404(Comment, id=comment_id)
        Like.objects.filter(user=request.user, comment=comment).delete()
        return Response({'message': 'Comment unliked'})


class FollowUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, user_id):
        user_to_follow = get_object_or_404(User, id=user_id)
        
        # Can't follow yourself
        if request.user.id == user_to_follow.id:
            return Response({'error': 'You cannot follow yourself'}, status=400)
        
        follow, created = Follow.objects.get_or_create(
            follower=request.user, 
            following=user_to_follow
        )
        
        if created:
            return Response({
                'message': f'Now following {user_to_follow.username}',
                'following': True
            })
        return Response({
            'message': f'Already following {user_to_follow.username}',
            'following': True
        })
    
    def delete(self, request, user_id):
        user_to_unfollow = get_object_or_404(User, id=user_id)
        
        deleted_count, _ = Follow.objects.filter(
            follower=request.user, 
            following=user_to_unfollow
        ).delete()
        
        if deleted_count > 0:
            return Response({
                'message': f'Unfollowed {user_to_unfollow.username}',
                'following': False
            })
        return Response({
            'message': f'Not following {user_to_unfollow.username}',
            'following': False
        })


class UserSearchView(generics.ListAPIView):
    serializer_class = UserSearchSerializer
    
    def get_serializer_context(self):
        return {'request': self.request}
    
    def get_queryset(self):
        query = self.request.GET.get('query', '').strip()
        
        if not query:
            return UserProfile.objects.none()
            
        # Find matching users
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
        
        # Get or create UserProfile for each user
        user_profiles = []
        for user in users:
            profile, created = UserProfile.objects.get_or_create(user=user)
            user_profiles.append(profile)
            
        return user_profiles

class NewsFeedView(generics.ListAPIView):
    serializer_class = PostSerializer
    
    def get_queryset(self):
        
        following_ids = self.request.user.follows.values_list('following_id', flat=True)
        return Post.objects.filter(user_id__in=following_ids).order_by('-created_at')
    

def home(request):
    return render(request, 'home.html')

def register_page(request):
    return render(request, 'register.html')

def login_page(request):
    return render(request, 'login.html')

def feed_page(request):
    return render(request, 'feed.html')

def logout(request):
    auth_logout(request)
    return redirect('home')

def profile_page(request):
    return render(request, 'profile.html')


def user_profile_page(request, username):
    profile_user = get_object_or_404(User, username=username)
    return render(request, 'user_profile.html', {'profile_user': profile_user})