"""impala URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from lessons import views
from datetime import datetime

urlpatterns = [
    path('admin/', admin.site.urls),

    # Pages for all logged in users
    path('', views.home, name='home'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('log_in/', views.log_in, name='log_in'),
    path('log_out/', views.log_out, name='log_out'),

    # Pages for students
    path('lessons/', views.lessons, name='lessons'),
    path('list_lessons/', views.list_lessons, name='list_lessons'),
    path('children/', views.children, name='children'),
    path('payments/', views.payments, name='payments'),
    path('invoice/<int:id>/', views.invoice, name='invoice'),
    path('edit_request/<int:id>/', views.edit_request, name='edit_request'),
    path('view_booking/<int:id>/', views.view_booking, name='view_booking'),

    #Pages for teachers
    path('schedule/', views.schedule , name='schedule',kwargs={'year':datetime.today().year, 'month': datetime.today().month}),
    path('schedule/<int:year>/<int:month>/', views.schedule , name='schedule_custom'),

    # Pages for admins
    path('manage_lessons/', views.manage_lessons, name='manage_lessons'),
    path('book_lesson/<int:id>/', views.book_lesson, name='book_lesson', kwargs={'type': 'req'}),
    path('book_lesson/new/', views.book_lesson, name='book_lesson_new', kwargs={'id': 'new', 'type':'new'}),
    path('book_lesson/user/<int:id>/', views.book_lesson, name='book_lesson_user', kwargs={'type': 'user'}),
    path('book_lesson/edit/<int:id>/', views.book_lesson, name='book_lesson_edit', kwargs={'type': 'edit'}),
    path('billing/', views.billing, name='billing'),
    path('terms/', views.terms, name='terms'),
    path('edit_term/<int:id>', views.edit_term, name='edit_term'),

    # Pages for super admins
    path('permissions/', views.permissions, name='permissions'),
    path('user/<int:id>/', views.user, name='user'),
    path('user/create/', views.user, name='create_user', kwargs={'id': 'create'}),
]
