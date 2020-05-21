from django.urls import path, include
from workout.views import WorkoutCreate, WorkoutDetail, WorkoutDelete, ExerciseDelete, ExerciseCreate

app_name = 'workout'

urlpatterns = [
    # path('', WorkoutIndex.as_view(), name='workout_index'),
    path('create', WorkoutCreate.as_view(), name='workout_create'),
    path('<int:pk>/', WorkoutDetail.as_view(), name='workout_detail'),
    path('workout_delete/<int:pk>/', WorkoutDelete.as_view(), name='workout_delete'),
    path('<int:pk>/exercise_delete/<int:exercise_pk>/', ExerciseDelete.as_view(), name='exercise_delete'),
    path('<int:pk>/exercise_add/', ExerciseCreate.as_view(), name='exercise_add'),
    # path('edit/<int:pk>/', WorkoutEdit.as_view(), name='workout_edit')
]
