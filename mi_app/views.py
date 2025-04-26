# mi_app/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer
from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import UserSerializer, UserDeleteSerializer, UserRegistrationSerializer
from rest_framework.exceptions import NotFound
from rest_framework import permissions
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime
from rest_framework.pagination import PageNumberPagination


##PROJECTS

class ProjectView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        objetos = Project.objects.filter(owner=self.request.user)
        name = request.query_params.get('name')
        if name is not None:
            objetos = objetos.filter(name=name)
        paginator = PageNumberPagination()
        paginated_projects = paginator.paginate_queryset(objetos,request)
        serializer = ProjectSerializer(paginated_projects, many=True)
        return paginator.get_paginated_response(serializer.data)


    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        usuario_id = self.request.user.id
        print(usuario_id)
        try:
            usuario = User.objects.get(id=usuario_id)
        except User.DoesNotExist:
            raise NotFound(detail="User Not found.")
        
        if serializer.is_valid():
            serializer.save(owner=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteProjectView(APIView):
    def delete(self, request,project_id):
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            raise NotFound("Project Not Found.")

        if project.owner != self.request.user:
            raise PermissionDenied("Unauthorized to delete this resource.")

        project.delete()
        return Response({"mensaje": "Project successfully deleted."}, status=status.HTTP_204_NO_CONTENT)

class UpdateProjectView(APIView):
    def patch(self,request,project_id):
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            raise NotFound("Project Not Found.")

        if project.owner != self.request.user:
            raise PermissionDenied("Unauthorized to edit this resource.")
        
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"mensaje": "Project successfully updated."}, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


##TASKS
class TaskView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        objetos = Task.objects.filter(project__owner=self.request.user)
        is_completed = request.query_params.get('is_completed')
        due_date_str = request.query_params.get('due_date')
        due_before_str = request.query_params.get('due_date_before')
        due_after_str = request.query_params.get('due_date_after')
        title = request.query_params.get('title')

        if is_completed is not None:
            if is_completed.lower() == 'true':
                objetos = objetos.filter(is_completed=True)
            elif is_completed.lower() == 'false':
                objetos = objetos.filter(is_completed=False)
        else:
            if due_before_str is not None:
                try:
                    date = datetime.strptime(due_before_str, "%Y-%m-%d").date()
                    objetos = objetos.filter(due_date__lte=date)
                except ValueError:
                    return Response({'error': 'Formato de fecha inválido. Usa YYYY-MM-DD.'}, status=400)
            if due_after_str is not None:
                try:
                    date = datetime.strptime(due_after_str, "%Y-%m-%d").date()
                    objetos = objetos.filter(due_date__gte=date)
                except ValueError:
                    return Response({'error': 'Formato de fecha inválido. Usa YYYY-MM-DD.'}, status=400)
        if title is not None:
            objetos = objetos.filter(title=title)
        paginator = PageNumberPagination()
        paginated_tasks = paginator.paginate_queryset(objetos,request)
        serializer = TaskSerializer(paginated_tasks, many=True)
        return paginator.get_paginated_response(serializer.data)
    

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            project = serializer.validated_data.get('project')
            try:
                project = Project.objects.get(id=project.id)
            except Project.DoesNotExist:
                raise NotFound(detail="Project Not Found.")
            
            if project.owner != self.request.user:
                raise PermissionDenied("Unauthorized to post a Task with this Project.")
            
            serializer.save(project=project)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DeleteTaskView(APIView):
    def delete(self, request,task_id):
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound("Task Not Found.")

        if task.project.owner != self.request.user:
            raise PermissionDenied("Unauthorized to delete this resource.")

        task.delete()
        return Response({"mensaje": "Task successfully deleted."}, status=status.HTTP_204_NO_CONTENT)
    
class UpdateTaskView(APIView):
    def patch(self,request,task_id):
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound("Task Not Found.")

        if task.project.owner != self.request.user:
            raise PermissionDenied("Unauthorized to update this resource.")
        
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"mensaje": "Task successfully updated."}, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

##USERS

class UserList(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        if self.request.user.is_superuser == False:
            raise PermissionDenied("Unauthorized to get this resource.")
        objetos = User.objects.all()
        serializer = UserSerializer(objetos, many=True)
        return Response(serializer.data)
    
    
class UserRegisterView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            access = str(refresh.access_token)
            refresh = str(refresh)
            return Response({
                "username":user.username,
                "email":user.email,
                "access":access,
                "refresh":refresh,
            }
            , status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        serializer = UserDeleteSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            email = serializer.validated_data.get('email')

            try:
                if username:
                    user = User.objects.get(username=username)
                    if username != self.request.user.username:
                        raise PermissionDenied("Unauthorized to delete this resource.")
                else:
                    user = User.objects.get(email=email)
                    if email != self.request.user.get_email_field_name():
                        raise PermissionDenied("Unauthorized to delete this resource.")

                user.delete()
                return Response({"detail": "User successfully deleted."}, status=status.HTTP_204_NO_CONTENT)
            except User.DoesNotExist:
                return Response({"detail": "Usuario Not Found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
