from django.db import models

# Create your models here.

class Employee(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    class Meta:
        db_table = 'Employee'


class Assignment(models.Model):

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='assignments')
    
    secret_child = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='secret_children')

    class Meta:
        db_table = 'Assignment'