from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name='login'),
    path('feed/', views.feed_page, name='feed'),
    path('logout/', views.logout, name='logout'),


    path('auth/register/', views.UserRegistrationView.as_view(), name='api-register'),
    path('auth/login/', views.UserLoginView.as_view(), name='api-login'),
    path('auth/logout/', views.UserLogoutView.as_view(), name='api-logout'),
    
    
    path('profiles/me/', views.UserProfileView.as_view(), name='my-profile'),
    path('profiles/<int:pk>/', views.UserProfileDetailView.as_view(), name='profile-detail'),
    
   
    path('posts/', views.PostListCreateView.as_view(), name='post-list'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:post_id>/comments/', views.CommentListCreateView.as_view(), name='comment-list'),
    
    
    path('posts/<int:post_id>/like/', views.LikePostView.as_view(), name='like-post'),
    path('comments/<int:comment_id>/like/', views.LikeCommentView.as_view(), name='like-comment'),
    
    
    path('users/<int:user_id>/follow/', views.FollowUserView.as_view(), name='follow-user'),
    
    
    path('search/users/', views.UserSearchView.as_view(), name='user-search'),
    path('api/feed/', views.NewsFeedView.as_view(), name='news-feed'),
]