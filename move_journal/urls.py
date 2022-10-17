from django.urls import path
from . import views

urlpatterns = [
    path("move/", views.CalculationView.as_view(), name='move_zhournal'),
    path("move_view/", views.MoveIntView.as_view(), name='move_view'),
    path('move_view/autocomplete/', views.AutoComplete.as_view(), name='auto_complete'), 
    path('post_quide/', views.PostQuide.as_view(), name='post-quide'),
    # path('change_quide/', views.ChangeQuide.as_view(), name='change-quide'),
    path('move_list/', views.MoveListView.as_view(), name='zhournal_list'),
    path('move_filter_list/', views.MoveFilterListView.as_view(),name='move_filter_list'),
    # path('create/', views.QuideCreateView.as_view(), name='create_quide'),
    path('move_quide_list/', views.MoveQuideList.as_view(), name='move_quide_list'),
]
