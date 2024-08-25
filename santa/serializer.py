from .models import *

from rest_framework import serializers

class EmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model=Employee
        fields='__all__'

class AssignmentSerializer(serializers.ModelSerializer):

    class Meta:
        model=Assignment
        fields='__all__'

class AssignmentSerializers(serializers.ModelSerializer):

    class Meta:
        model=Assignment
        fields='__all__'
        depth = 1

        