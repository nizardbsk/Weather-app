from django.urls import path
from . import views

urlpatterns=[
    path('',views.home,name='home'),
    path('add-city-page/',views.addcitypage,name='add-city-page'),
    path('comparison-page/',views.compare,name='comparison-page'),
    path('city/<str:city_id>/',views.citypage,name='city-page'),
    path('profile-page/<str:profile_id>/',views.profilepage,name='profile-page'),
    path('update-profile/<str:profile_id>/',views.updateprofile,name='update-profile'),
    path('compare-with/<str:city1_id>/<str:city2_id>/',views.comparewith,name='compare-with'),
]