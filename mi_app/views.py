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


##PROJECTS

class ProjectView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        objetos = Project.objects.filter(owner=self.request.user)
        serializer = ProjectSerializer(objetos, many=True)
        return Response(serializer.data)

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
        serializer = TaskSerializer(objetos, many=True)
        return Response(serializer.data)
    

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
