from django.shortcuts import render, redirect
import requests 
from .forms import LoginForm, RegisterForm, NewTaskForm
import os
from dotenv import load_dotenv

load_dotenv()
# Create your views here.

API_URL = os.getenv("API_URL")
API_TASKS = os.getenv("API_TASKS")

def home(request):
    session = request.session.items()
    session_dict = {k: v for k, v in session}
    user = session_dict.get("user_id", None)


    if user is not None:
        user_dict = api_request(request, "GET", f"{API_URL}/user/{user}")
        
        if user_dict and user_dict.status_code == 200:
            user_data = user_dict.json()
            
            return render(request, 'app/index.html', {'user': user_data})

    return render(request, 'app/index.html')

def all_users(request):
    
    response = requests.get(f"{API_URL}/users")
    
    users = response.json() if response.status_code == 200 else []
    
    return render(request, 'app/all_u.html', {'users': users})

#Sing in
def login_view(request):
    
    form = LoginForm()
    
    if request.method == 'POST':
        
        form = LoginForm(request.POST)
        
        if form.is_valid():
            
            email = form.cleaned_data['email']            
            password = form.cleaned_data['password']
            
            response = requests.post(f"{API_URL}/auth/login", json={'email': email, 'password': password})
            
            if response.status_code == 200:

                data = response.json()
                

                request.session["user_id"] = data["user_id"]
                print("USER_ID:", request.session.get("user_id"))
                request.session["access"] = data["access_token"]                
                request.session["refresh"] = data["refresh_token"]
                

                request.session.modified = True

                return redirect('index')
            return redirect('login')
    return render(request, 'app/login.html', {'form': form})

#Sign up
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():

            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']            
            confirm_password = form.cleaned_data['confirm_password']
            
            if password != confirm_password:
            
                form.add_error('confirm_password', 'Passwords do not match')
            
            else:
            
                response = requests.post(f"{API_URL}/auth/register", json={'name': name, 'email': email, 'password': password})
            
                if response.status_code in (200, 201):
            
                    return render(request, 'app/register_success.html', {'message': 'Registration successful!'})
            
                else:
            
                    form.add_error(None, 'Registration failed')
    else:
        form = RegisterForm()
    return render(request, 'app/register.html', {'form': form})

#Logout
def logout_view(request):
    
    request.session.flush()
    
    return redirect('index')

#generic API request REQUIRES AUTHENTICATION
def api_request(request, method, url, data=None):

    access = request.session.get("access")
    refresh = request.session.get("refresh")

    if not access:
        return None

    headers = {
        "Authorization": f"Bearer {access}"
    }

    r = requests.request(method, url, json=data, headers=headers)

    # if token expired, try refresh
    if r.status_code == 401 and refresh:

        refresh_resp = requests.post(
            f"{API_URL}/auth/refresh",
            json={"refresh_token": refresh}
        )

        if refresh_resp.status_code == 200:

            new_access = refresh_resp.json()["access_token"]
            request.session["access"] = new_access
            headers["Authorization"] = f"Bearer {new_access}"

            # Retry
            r = requests.request(method, url, json=data, headers=headers)

        else:
            request.session.flush()
            return None

    return r

#create new task
def newTask_view(request):

    session = request.session.items()
    session_dict = {k: v for k, v in session}
    user = session_dict.get("user_id", None)
    
    username = api_request(request, "GET", f"{API_URL}/user/{user}")
    
    un = username.json()['name'] if username and username.status_code == 200 else "User"
    form = NewTaskForm()
    
    if request.method == 'POST':
        
        form = NewTaskForm(request.POST)
        
        if form.is_valid():
            
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            completed = form.cleaned_data['completed']
            
            data = {
                'title': title,
                'description': description,
                'completed': completed
            }
            
            response = api_request(request, "POST", API_TASKS, data)
            
            if response and response.status_code == 200:
                
                return redirect('tasks')
    
    return render(request, 'app/newTask.html', {'form': form, 'user': un})

#update task
def upd_task_view(request, task_id):

    session = request.session.items()
    session_dict = {k: v for k, v in session}
    user = session_dict.get("user_id", None)
    
    username = api_request(request, "GET", f"{API_URL}/user/{user}")
    
    un = username.json()['name'] if username and username.status_code == 200 else "User"
    
    task_resp = api_request(request, "GET", f"{API_TASKS}{task_id}")
    
    if not task_resp or task_resp.status_code != 200:
        return redirect('index')
    
    task_data = task_resp.json()
    
    form = NewTaskForm(initial={
        'title': task_data['title'],
        'description': task_data['description'],
        'completed': task_data['completed']
    })
    
    if request.method == 'POST':
        
        form = NewTaskForm(request.POST)
        
        if form.is_valid():
            
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            completed = form.cleaned_data['completed']
            
            data = {
                'title': title,
                'description': description,
                'completed': completed
            }
            
            response = api_request(request, "PUT", f"{API_TASKS}{task_id}", data)
            
            if response and response.status_code == 200:
                
                return redirect('tasks')
    
    return render(request, 'app/upd_task.html', {'form': form, 'task_id': task_id, 'user': un})

#all tasks
def tasks_view(request):
    
    session = request.session.items()
    session_dict = {k: v for k, v in session}
    user = session_dict.get("user_id", None)
    
    username = api_request(request, "GET", f"{API_URL}/user/{user}")

    un = username.json()['name'] if username and username.status_code == 200 else "User"
    
    response = requests.get(API_TASKS)
    
    tasks = response.json() if response and response.status_code == 200 else []
    
    return render(request, 'app/tasks.html', {'tasks': tasks, 'user': un})

#delete task
def delete_task_view(request, task_id):
    
    response = api_request(request, "DELETE", f"{API_TASKS}{task_id}")
    
    return redirect('tasks')