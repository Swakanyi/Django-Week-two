from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.contrib.auth import login, logout
from .models import User, UserProfile, Post, Comment, Like, Follow
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    PostSerializer, CommentSerializer, LikeSerializer, FollowSerializer
)
from django.shortcuts import render

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
        return self.request.user.user_profile

class UserProfileDetailView(generics.RetrieveAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
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
    def post(self, request, user_id):
        user_to_follow = generics.get_object_or_404(User, id=user_id)
        follow, created = Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
        
        if created:
            return Response({'message': f'Now following {user_to_follow.username}'}, status=status.HTTP_201_CREATED)
        return Response({'message': f'Already following {user_to_follow.username}'}, status=status.HTTP_200_OK)
    
    def delete(self, request, user_id):
        user_to_unfollow = generics.get_object_or_404(User, id=user_id)
        Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
        return Response({'message': f'Unfollowed {user_to_unfollow.username}'})


class UserSearchView(generics.ListAPIView):
    serializer_class = UserProfileSerializer
    
    def get_queryset(self):
        query = self.request.GET.get('query', '')
        return UserProfile.objects.filter(
            Q(user__username__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)
        )

class NewsFeedView(generics.ListAPIView):
    serializer_class = PostSerializer
    
    def get_queryset(self):
        # Get posts from users that the current user follows
        following_ids = self.request.user.follows.values_list('following_id', flat=True)
        return Post.objects.filter(user_id__in=following_ids).order_by('-created_at')
    

def home(request):
    return render(request, 'home.html')