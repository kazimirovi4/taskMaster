from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'

    def __str__(self):
        return self.name



class Task(models.Model):
    title = models.CharField(max_length=100, null=True, verbose_name="Название")
    responsible = models.ForeignKey(User, related_name='responsible_tasks', on_delete=models.SET_NULL, null=True,
                                    blank=True, verbose_name="Ответственный")
    content = models.CharField(max_length=1000, null=True, blank=True, verbose_name="Описание")
    date_posted = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Дата создания")
    due_date = models.DateTimeField(null=True, blank=True, verbose_name="Срок выполнения")
    priority = models.CharField(max_length=1, choices=[('L', 'Низкий'), ('M', 'Средний'), ('H', 'Высокий')],
                                default='M', verbose_name="Приоритет")
    status = models.CharField(max_length=2, choices=[('N', 'Новый'), ('IP', 'В процессе'), ('C', 'Завершен')],
                              default='N', verbose_name="Статус")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Проект")
    user = models.ForeignKey(User, max_length=20, on_delete=models.CASCADE, null=True, verbose_name="Создатель")

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def __str__(self):
        return self.title



class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name='Задача')
    message = models.CharField(max_length=255, verbose_name='Сообщение')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'

    def __str__(self):
        return self.user.username


class UserNotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    email_notifications = models.BooleanField(default=True, verbose_name='Уведомления по Email')
    sms_notifications = models.BooleanField(default=False, verbose_name='Уведомления по SMS')
    push_notifications = models.BooleanField(default=False, verbose_name='Push-уведомления')

    class Meta:
        verbose_name = 'Настройки уведомлений пользователя'
        verbose_name_plural = 'Настройки уведомлений пользователей'

    def __str__(self):
        return self.user.username


class Comment(models.Model):
    task = models.ForeignKey(Task, related_name='comments', on_delete=models.CASCADE, verbose_name='Задача')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    content = models.TextField(verbose_name='Содержание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.user.username