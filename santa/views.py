from django.shortcuts import render

from .models import *

from .serializer import *

from rest_framework.views import APIView

from rest_framework.response import Response

from django.http import HttpResponse,JsonResponse

from rest_framework.renderers import JSONRenderer

import json


from rest_framework import status

import os

import pandas as pd

import random

import copy



# Create your views here.

class EmployeeListView(APIView):

    def get(self, request, *args, **kwargs):
        try:
            data = request.query_params
            module = Employee.objects.all()
            serializer = EmployeeSerializer(module,many=True)
            output = JSONRenderer().render(serializer.data)
            return HttpResponse(output, content_type='application/json',status=status.HTTP_200_OK)
        except Exception as e:
            output = JSONRenderer().render({"Error": str(e)})
            return HttpResponse(output, content_type='application/json', status=status.HTTP_400_BAD_REQUEST)

    def post(self,request,*args,**kwargs):
    
        new_data = request.FILES
        file_key = next(iter(request.FILES), None)
        if not file_key:
            output = JSONRenderer().render({"Error": "No file provided"})
            return HttpResponse(output, content_type='application/json', status=status.HTTP_400_BAD_REQUEST)

        new_data = request.FILES[file_key]
        if not os.path.splitext(new_data.name)[1] == '.xlsx':
            output = JSONRenderer().render("Wrong Format")
            return HttpResponse(output, content_type='application/json')
        df = pd.read_excel(new_data, header=None, skiprows=1)
        # Remove empty rows
        df.dropna(how='all', inplace=True)
        df.columns = ['Employee_Name','Employee_EmailID']
        imported_data = df.values.tolist()
        if not imported_data or len(imported_data[0]) < 2:
            output = JSONRenderer().render({"Error": "Empty file or insufficient columns"})
            return HttpResponse(output, content_type='application/json', status=status.HTTP_400_BAD_REQUEST)
        print("len",len(imported_data))
        for i, data in enumerate(imported_data, start=2):
            print("data",data)
            try:
                value = Employee.objects.create(
                    name=data[0],
                    email=data[1],
                )
               
            except Exception as e:
                output = JSONRenderer().render({"Error": str(e)})
                return HttpResponse(output, content_type='application/json', status=status.HTTP_400_BAD_REQUEST)
        
        
        return JsonResponse({"Result":"Uploaded Successfully"})


    
    # Assignment 



class AssignmentTaskList(APIView):

    def get(self, request, *args, **kwargs):
        try:
            data = request.query_params
            new_assignment=Assignment.objects.all()
            # Serialize the response
            assignment_serializer = json.dumps(AssignmentSerializers(new_assignment, many=True).data)
            print("assignment_serializer",assignment_serializer)
            listemployee=json.loads(assignment_serializer)
            # print("listemployee",listemployee)
            li=[{'Employee_Name':i['employee']['name'],"Employee_EmailID":i['employee']['email'],"Secret_Child_Name":i['secret_child']['name'],"Secret_Child_EmailID":i['secret_child']['email']}for i in listemployee ]
            return Response(li, status=status.HTTP_201_CREATED)
        except Exception as e:
            output = JSONRenderer().render({"Error": str(e)})
            return HttpResponse(output, content_type='application/json', status=status.HTTP_400_BAD_REQUEST)
        
    def post(self, request):
        # Get the Excel file from the request
        new_data = request.FILES
        file_key = next(iter(request.FILES), None)
        if not file_key:
            output = JSONRenderer().render({"Error": "No file provided"})
            return HttpResponse(output, content_type='application/json', status=status.HTTP_400_BAD_REQUEST)
        new_data = request.FILES[file_key]
        if not os.path.splitext(new_data.name)[1] == '.xlsx':
                output = JSONRenderer().render("Wrong Format")
                return HttpResponse(output, content_type='application/json')
        print("new_data",new_data)
        try:
            # Read the Excel file into a DataFrame
            df = pd.read_excel(new_data, header=None, skiprows=1)
            df.dropna(how='all', inplace=True)  # Remove empty rows
            df.columns = ['Employee_Name', 'Employee_EmailID', 'Secret_Child_Name', 'Secret_Child_EmailID']

            # Convert DataFrame to a list of dictionaries for previous assignments
            previous_assignments = [
                {
                    "employee_name": row['Employee_Name'],
                    "employee_email": row['Employee_EmailID'],
                    "secret_child_name": row['Secret_Child_Name'],
                    "secret_child_email": row['Secret_Child_EmailID'],
                }
                for _, row in df.iterrows()
            ]
            # print("previous_assignments",previous_assignments)
            # Fetch all current employees from the database and serialize them
            module = Employee.objects.all()
            serializer = json.dumps(EmployeeSerializer(module, many=True).data)
            current_year_employees = json.loads(serializer)
            # print("current_year_employees",current_year_employees)
            # Initialize the SecretSanta class with current employees and previous assignments
            santa = SecretSanta(current_year_employees, previous_assignments)

            # Perform the assignment
            new_assignments = santa.assign()
            # print("new_assignments",new_assignments)
            # Save the new assignments
            for assignment in new_assignments:
                assignment.save()

            new_assignment=Assignment.objects.all()
            # Serialize the response
            assignment_serializer = json.dumps(AssignmentSerializers(new_assignment, many=True).data)
            print("assignment_serializer",assignment_serializer)
            listemployee=json.loads(assignment_serializer)
     
            # print("listemployee",listemployee)
            li=[{'Employee_Name':i['employee']['name'],"Employee_EmailID":i['employee']['email'],"Secret_Child_Name":i['secret_child']['name'],"Secret_Child_EmailID":i['secret_child']['email']}for i in listemployee ]
            return Response({"Assinment":li,"EmployeeList":previous_assignments}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class SecretSanta:
    def __init__(self, employees, previous_assignments):
        self.employees = list(employees)  # List of current year employees
        self.previous_assignments = previous_assignments  # List of dictionaries from previous year

    def assign(self):
        # Create a mapping of employee names to previous secret children
        previous_map = {a['employee_name']: a['secret_child_name'] for a in self.previous_assignments}
        
        # Create a list of available employees for assignment
        available_employees = [e['name'] for e in self.employees]
        
        # Create a mapping of employee names to their ID
        employee_id_map = {e['name']: e['id'] for e in self.employees}
        
        # Create a dictionary for the results
        assignments = []

        # Iterate over each employee
        for employee in self.employees:
            employee_name = employee['name']
            # Remove the current employee from the available list
            if employee_name in available_employees:
                available_employees.remove(employee_name)
            
            # Determine the previous secret child for this employee
            previous_secret_child = previous_map.get(employee_name)
            
            # Remove the previous secret child from the available list if applicable
            if previous_secret_child and previous_secret_child in available_employees:
                available_employees.remove(previous_secret_child)
                
            # Check if there are any available secret children left
            if not available_employees:
                raise Exception(f"No valid secret child for {employee_name}")
            
            # Choose the first available employee as the secret child
            secret_child_name = available_employees[0]
            secret_child_id = employee_id_map[secret_child_name]

            # Create a new assignment object
            assignment = Assignment(
                employee_id=employee_id_map[employee_name],
                secret_child_id=secret_child_id
            )
            assignments.append(assignment)

            # Add the secret child back to the available list for the next iterations
            available_employees.append(secret_child_name)

        return assignments