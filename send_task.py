from celery import Celery

app = Celery('onai-school')

# Configure Redis as the broker
app.conf.broker_url = 'redis://195.49.215.16:6379/0'

# Other optional configurations (result backend, task settings, etc.)
app.conf.result_backend = 'redis://195.49.215.16:6379/0'
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']

x = app.send_task("apps.users.tasks.send_student_data", queue="onai-tasks")
