from django.urls import path

from .views import *


urlpatterns = [
    path("employee/",EmployeeListView.as_view()),
    
    path("AssignmentTaskList/",AssignmentTaskList.as_view()),


]