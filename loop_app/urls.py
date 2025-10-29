from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('auth/register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('auth/logout/', views.UserLogoutView.as_view(), name='logout'),
    
    
    path('profiles/me/', views.UserProfileView.as_view(), name='my-profile'),
    path('profiles/<int:pk>/', views.UserProfileDetailView.as_view(), name='profile-detail'),
    
   
    path('posts/', views.PostListCreateView.as_view(), name='post-list'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:post_id>/comments/', views.CommentListCreateView.as_view(), name='comment-list'),
    
    
    path('posts/<int:post_id>/like/', views.LikePostView.as_view(), name='like-post'),
    path('comments/<int:comment_id>/like/', views.LikeCommentView.as_view(), name='like-comment'),
    
    
    path('users/<int:user_id>/follow/', views.FollowUserView.as_view(), name='follow-user'),
    
    
    path('search/users/', views.UserSearchView.as_view(), name='user-search'),
    path('feed/', views.NewsFeedView.as_view(), name='news-feed'),
]