from django.contrib import auth
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import CreateUserForm, LoginForm, CreateProjectForm, CreateTaskForm, TaskFilterForm, CommentForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Project, Task, Notification, UserNotificationPreference
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group
from django.core.mail import send_mail




def is_admin(user):
    return user.groups.filter(name='Администратор').exists()


def home(request):
    return render(request, 'index.html')


def register(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.email = form.cleaned_data['email']
            user.save()

            user_group = Group.objects.get(name='Обычный пользователь')
            user.groups.add(user_group)

            messages.success(request, 'Регистрация пользователя прошла успешно!')
            return redirect('user-login')
    context = {'form': form}
    return render(request, 'register.html', context=context)


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                user = User.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('dashboard')
                else:
                    form.add_error('password', 'Не правильно введен пароль')
            except User.DoesNotExist:
                form.add_error('email', 'Пользователя не существует.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


@login_required(login_url='user-login')
def dashboard(request):
    return render(request, 'profile/dashboard.html')


@user_passes_test(is_admin)
@login_required(login_url='user-login')
def createProject(request):
    form = CreateProjectForm()
    if request.method == 'POST':
        form = CreateProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('view-projects')
    context = {'form': form}
    return render(request, 'profile/create-project.html', context=context)


@login_required(login_url='user-login')
def viewProjects(request):
    projects = Project.objects.all()
    context = {'projects': projects}
    return render(request, 'profile/view-projects.html', context=context)



@login_required(login_url='user-login')
def createTask(request):
    form = CreateTaskForm()
    if request.method == 'POST':
        form = CreateTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            form.save()

            notification_message = f'Новая задача создана: {task.title}'
            Notification.objects.create(user=task.responsible, task=task, message=notification_message)

            return redirect('view-task')
    context = {'form': form}
    return render(request, 'profile/create-task.html', context=context)


@login_required(login_url='user-login')
def updateTask(request, pk):
    task = Task.objects.get(id=pk)
    form = CreateTaskForm(instance=task)
    if request.method == 'POST':
        form = CreateTaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('view-task')
    context = {'form': form}
    return render(request, 'profile/update-task.html', context=context)


@login_required(login_url='user-login')
def viewTask(request):
    current_user = request.user
    if is_admin(current_user):
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(user=current_user) | Task.objects.filter(responsible=current_user)
    form = TaskFilterForm(request.GET or None)

    if request.GET and form.is_valid():
        status = form.cleaned_data.get('status')
        priority = form.cleaned_data.get('priority')
        project = form.cleaned_data.get('project')

        if status:
            tasks = tasks.filter(status=status)
        if priority:
            tasks = tasks.filter(priority=priority)
        if project:
            tasks = tasks.filter(project=project)

    context = {'task': tasks, 'form': form}
    return render(request, 'profile/view-tasks.html', context=context)


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    comments = task.comments.all()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.user = request.user
            comment.save()
            return redirect('task-detail', pk=task.pk)
    else:
        form = CommentForm()
    return render(request, 'profile/task_detail.html', {'task': task, 'comments': comments, 'form': form})


@login_required
def viewTasksByProject(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    tasks = Task.objects.filter(project=project, user=request.user)
    context = {'tasks': tasks, 'project': project}
    return render(request, 'profile/view-tasks.html', context)


@login_required(login_url='user-login')
def deleteTask(request, pk):
    task = Task.objects.get(id=pk)
    if request.method == 'POST':
        task.delete()
        return redirect('view-task')
    return render(request, 'profile/delete-task.html')

def user_logout(request):
    auth.logout(request)
    return redirect('home')


def send_notification(notification):
    send_mail(
        'Уведомление о задаче',
        notification.message,
        'from@example.com',
        [notification.user.email],
        fail_silently=False,
    )


@login_required
def notification_preferences(request):
    user = request.user
    preferences, created = UserNotificationPreference.objects.get_or_create(user=user)

    if request.method == 'POST':
        preferences.email_notifications = request.POST.get('email_notifications') == 'on'
        preferences.sms_notifications = request.POST.get('sms_notifications') == 'on'
        preferences.push_notifications = request.POST.get('push_notifications') == 'on'

        try:
            preferences.save()
            messages.success(request, 'Настройки уведомлений успешно обновлены.')
        except ValidationError as e:
            messages.error(request, f'Ошибка: {e}')

        return redirect('notification-preferences')

    context = {
        'preferences': preferences
    }
    return render(request, 'profile/notification_preferences.html', context)


@login_required
def calendar_view(request):
    current_user = request.user
    if is_admin(current_user):
        tasks = Task.objects.all().values('title', 'due_date')
    else:
        tasks = Task.objects.filter(user=current_user).values('title', 'due_date') | Task.objects.filter(
            responsible=current_user).values('title',
                                             'due_date')

    return render(request, 'profile/calendar.html', {'tasks': tasks})


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    comments = task.comments.all()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.user = request.user
            comment.save()
            return redirect('task-detail', pk=task.pk)
    else:
        form = CommentForm()
    return render(request, 'profile/task_detail.html', {'task': task, 'comments': comments, 'form': form})