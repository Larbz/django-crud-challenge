# mi_app/serializers.py
from rest_framework import serializers
from .models import Project
from .models import Task
from django.contrib.auth.models import User
 

#PROJECT

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        exclude = ['owner']
        read_only_fields = ['created_at']

#TASK

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['created_at']

#USER

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email','password']
        extra_kwargs = {'password': {'write_only': True}}
        
class UserDeleteSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    def validate(self, data):
        if not data.get('username') and not data.get('email'):
            raise serializers.ValidationError("Must provide a valid username or email.")
        return data
    
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False,default="")
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data.get('email')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
