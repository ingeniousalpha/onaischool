from django.db.models import Sum, Count, Func
from django.shortcuts import render
from rest_framework.generics import ListAPIView, GenericAPIView
from django.conf import settings
from django.utils import timezone

from apps import Roles
from apps.analytics.models import Quiz
from apps.common.mixins import PublicJSONRendererMixin
from rest_framework.response import Response

from apps.content.models import School
from apps.location.models import City
from apps.users.models import User, UserQuizReport, UserQuizQuestion

MONTHS_NAMES = {
    "1": "Январь",
    "2": "Февраль",
    "3": "Март",
    "4": "Апрель",
    "5": "Май",
    "6": "Июнь",
    "7": "Июль",
    "8": "Август",
    "9": "Сентябрь",
    "10": "Октябрь",
    "11": "Ноябрь",
    "12": "Декабрь"
}


class MonthYear(Func):
    function = 'CONCAT'
    template = "%(function)s(EXTRACT(YEAR FROM %(expressions)s), '.', EXTRACT(MONTH FROM %(expressions)s))"


def get_month_str(month_dot_year):
    year, month = month_dot_year.split('.')
    return f"{MONTHS_NAMES.get(month)} {year}"


def dashboard_view(request):
    period = request.GET.get('period')  # today/last_week/last_month/last_year
    group_by_field = 'created_at__date'
    if period == 'today':
        filter_period = timezone.now().date()
    elif period == 'last_week':
        filter_period = timezone.now() - timezone.timedelta(days=7)
    elif period == 'last_year':
        group_by_field = 'month_year'
        filter_period = timezone.now() - timezone.timedelta(days=365)
    else:
        period = 'last_month'
        filter_period = timezone.now() - timezone.timedelta(days=30)

    users_total = User.objects.filter(created_at__gte=filter_period)
    users_count_total = users_total.count()
    students_count_total = users_total.filter(role=Roles.STUDENT).count()
    cities = City.objects.all()

    if period == 'last_year':
        users_dates = users_total.annotate(month_year=MonthYear('created_at')).values(group_by_field).annotate(
            users_count=Count('id')).order_by(group_by_field)
    else:
        users_dates = users_total.values(group_by_field).annotate(users_count=Count('id')).order_by(group_by_field)

    users_dates_list = []
    users_count_list = []
    for item in users_dates:
        users_dates_list.append(get_month_str(item[group_by_field]) if period == "last_year" else item[group_by_field])
        users_count_list.append(item['users_count'])

    return render(request, "dashboard.html", {
        "period": period,
        "cities": cities,
        "users_count_total": users_count_total,
        "students_count_total": students_count_total,
        "users_dates_list": users_dates_list,
        "users_count_list": users_count_list
    })


from django.http import JsonResponse


def get_schools(request):
    region_id = request.GET.get('region_id')
    schools = School.objects.filter(city_id=region_id).values('id', 'name')
    return JsonResponse(list(schools), safe=False)


def get_students(request):
    school_id = request.GET.get('school_id')
    students = User.objects.filter(school_id=school_id).values('id', 'full_name', 'mobile_phone')
    return JsonResponse(list(students), safe=False)


def get_tasks_data(request):
    period = request.GET.get('task_period')  # today/last_week/last_month/last_year
    group_by_field = 'created_at__date'
    if period == 'today':
        filter_period = timezone.now().date()
    elif period == 'last_week':
        filter_period = timezone.now() - timezone.timedelta(days=7)
    elif period == 'last_year':
        group_by_field = 'month_year'
        filter_period = timezone.now() - timezone.timedelta(days=365)
    else:
        period = 'last_month'
        filter_period = timezone.now() - timezone.timedelta(days=30)

    region_id = request.GET.get('region_id')
    school_id = request.GET.get('school_id')
    student_id = request.GET.get('student_id')

    user_questions = UserQuizQuestion.objects.all()

    if region_id and region_id != 'all':
        user_questions = user_questions.filter(user__school__city_id=region_id)

    if school_id and school_id != 'all':
        user_questions = user_questions.filter(user__school_id=school_id)

    if student_id and student_id != 'all':
        user_questions = user_questions.filter(user_id=student_id)

    users_dates_list = []
    user_tasks_list = []

    user_resolved_tasks = user_questions.annotate(month_year=MonthYear('created_at')).values(group_by_field).annotate(
        resolved_task_count=Count('id')).order_by(
        group_by_field)

    for item in user_resolved_tasks:
        users_dates_list.append(item[group_by_field])
        user_tasks_list.append(item['resolved_task_count'])

    tasks_solved = user_questions.filter(created_at__gte=filter_period).count()
    tasks_correct = user_questions.filter(is_correct=True, created_at__gte=filter_period).count()

    data = {
        'users_dates_list': users_dates_list,
        'user_tasks_list': user_tasks_list,
        'tasks_solved': tasks_solved,
        'tasks_correct': tasks_correct,
        'percent_correct': (tasks_correct / tasks_solved) * 100 if tasks_solved > 0 else 0
    }

    return JsonResponse(data)
