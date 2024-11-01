from django.contrib.auth.models import User
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms.widgets import PasswordInput, EmailInput

from .models import Project, Task, Comment


class CreateUserForm(UserCreationForm):
    email = forms.EmailField(widget=EmailInput(), label="Email")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=PasswordInput)



class CreateTaskForm(forms.ModelForm):
    due_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), required=False,
                                   label="Срок выполнения")
    responsible = forms.ModelChoiceField(queryset=User.objects.all(), required=False, label="Ответственный")

    class Meta:
        model = Task
        fields = ['title', 'content', 'due_date', 'priority', 'status', 'project', 'responsible']
        exclude = ['user']


class CreateProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']


class TaskFilterForm(forms.Form):
    status = forms.ChoiceField(choices=[('', '---------')] + list(Task._meta.get_field('status').choices),
                               required=False, label="Статус")
    priority = forms.ChoiceField(choices=[('', '---------')] + list(Task._meta.get_field('priority').choices),
                                 required=False, label="Приоритет")
    project = forms.ModelChoiceField(queryset=Project.objects.all(), required=False, label="Проект")

    class Meta:
        model = Task
        fields = ['status', 'priority', 'project']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']