from django.urls import path
from .views import LogCreate, LogDetail, LogExerciseSetAdd, LogClose, SetDelete, StatisticsView

app_name = 'log'

urlpatterns = [
    path('log_create/<int:pk>', LogCreate.as_view(), name='log_create'),
    path('<int:log_pk>/', LogDetail.as_view(), name='log_detail'),
    path('<int:log_pk>/add_set/<int:exercise_pk>/', LogExerciseSetAdd.as_view(), name='log_exercise_set_add'),
    path('<int:log_pk>/close', LogClose.as_view(), name='log_close'),
    path('<int:log_pk>/delete_set/<int:exercise_pk>/set_number/<int:set_pk>', SetDelete.as_view(), name='set_delete'),
    path('statistics/', StatisticsView.as_view(), name='statistics'),
]
