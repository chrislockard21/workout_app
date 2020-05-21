from django.urls import path
from .views import ProfileIndex, ORMEdit, History

app_name = 'user_profile'

urlpatterns = [
    path('', ProfileIndex.as_view(), name='profile_index'),
    path('ORM_bulk_edit', ORMEdit.as_view(), name='orm_bulk_edit'),
    path('history', History.as_view(), name='history'),
]
