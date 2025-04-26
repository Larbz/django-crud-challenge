# 🎯 Objective:
Developed a RESTful API using Python and Django Rest Framework that manages a simple
system of Projects and Tasks, including authentication and authorization.
# 📂 Project Overview:
Built an API for managing projects and their associated tasks.
- Each User can create multiple Projects.
- Each Project can have multiple Tasks.
- Users can only manage their own Projects and Tasks.

# Project Setup:
1. Clone the repository on local
2. Create a virtual environment
```
python -m venv venv
```
Note: The environment will be created with the version of python you have installed.
3. Activate the virtual environment
``` 
source venv/bin/activate
```
4. Install dependencies
```
pip install -r requirements.txt
```
5. Apply migrations
```
python manage.py migrate
```
6. Start application
```
python manage.py runserver
```