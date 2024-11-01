from django.contrib import admin
from .models import Project, Task, Notification, Comment
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


admin.site.register(Task)
admin.site.register(Project)
admin.site.register(Notification)
admin.site.register(Comment)



def create_user_groups():
    admin_group, created = Group.objects.get_or_create(name='Администратор')
    user_group, created = Group.objects.get_or_create(name='Обычный пользователь')
    content_type = ContentType.objects.get_for_model(Task)
    view_task_permission = Permission.objects.get(codename='view_task', content_type=content_type)
    user_group.permissions.add(view_task_permission)
    all_permissions = Permission.objects.filter(content_type=content_type)
    admin_group.permissions.set(all_permissions)

# create_user_groups()