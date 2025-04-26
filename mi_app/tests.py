from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User

class A_AuthTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", password="12345678")
        
    def test_1(self):#register
        url = reverse('user-register')
        data = {"username": "test2", "password": "12345678"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_2(self):#login
        url = reverse('login')
        data = {"username": "test", "password": "12345678"}
        response = self.client.post(url, data)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class B_ProjectTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", password="12345678")
        url = reverse('login')
        data = {"username": "test", "password": "12345678"}
        response = self.client.post(url, data)
        self.token = response.data['access']
     
    def test_1(self):#CREATE PROJECT
        url = reverse('project-list')
        data = {
            "name":"Proyecto 1",
            "description":"Description 1"
        }
        print("Token",self.token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
     
    def test_2(self):#GET PROJECTS
        url = reverse('project-list')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class C_TaskTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", password="12345678")
        url = reverse('login')
        data = {"username": "test", "password": "12345678"}
        response = self.client.post(url, data)
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        url = reverse('project-list')
        data = {
            "name":"Proyecto 1",
            "description":"Description 1"
        }
        response = self.client.post(url, data)
        self.project_id = response.data['id']
     
    def test_1(self):#CREATE TASK
        url = reverse('task-list')
        data = {
            "title": "Task N",
            "description": "Descricion",
            "due_date": "2025-04-30",
            "project": self.project_id
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
     
    def test_2(self):#GET TASKS
        url = reverse('task-list')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)