import uuid as uuid_lib
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from phonenumber_field.modelfields import PhoneNumberField

from config.settings import Languages
from .managers import UserManager

from .. import Grades, Roles


class User(PermissionsMixin, AbstractBaseUser):
    class Meta:
        verbose_name = _("Учетная запись")
        verbose_name_plural = _("Учетная запись")

    uuid = models.UUIDField("UUID пользователя", default=uuid_lib.uuid4, unique=True)
    email = models.EmailField("Почта", max_length=40, unique=True)
    full_name = models.CharField("Имя", max_length=256, null=True, blank=True)
    mobile_phone = PhoneNumberField("Моб. телефон", blank=True, null=True)
    secret_key = models.UUIDField("Секретный ключ", default=uuid_lib.uuid4, unique=True)
    language = models.CharField(max_length=20, choices=Languages.choices, default=Languages.KAZAKH, verbose_name="Язык")
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_("Родитель")
    )
    grade = models.CharField(max_length=3, choices=Grades.choices, default=Grades.FIRST, verbose_name="Класс")
    role = models.CharField(max_length=50, choices=Roles.choices, default=Roles.STUDENT)
    is_active = models.BooleanField("Активный", default=True)
    is_staff = models.BooleanField("Сотрудник", default=False)
    is_email_confirmed = models.BooleanField("Почта подтверждена", default=False)
    is_mobile_phone_verified = models.BooleanField(default=False)
    avatar_image = models.ImageField(null=True, blank=True)
    created_at = models.DateTimeField(_("Создан"), default=timezone.now)
    updated_at = models.DateTimeField(_("Обновлен"), auto_now=True)

    USERNAME_FIELD = "email"
    objects = UserManager()

    def __str__(self):
        return str(self.mobile_phone or self.email)

    # @property
    # def username(self):
    #     if self.mobile_phone:
    #         return str(self.mobile_phone)
    #     return self.email

    def has_perm(self, perm, obj=None):
        if not self.is_active:
            return False
        if self.is_superuser:
            return True
        return perm in self.get_all_permissions(obj)

    def has_module_perms(self, app_label):
        if self.is_superuser:
            return True
        return self.is_active and any(
            perm[: perm.index(".")] == app_label for perm in self.get_all_permissions()
        )

    # def get_username(self):
    #     return self.mobile_phone

    def set_password(self, raw_password):
        super(User, self).set_password(raw_password)

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

    def set_active(self):
        self.is_active = True
        self.is_email_confirmed = True
        self.save(update_fields=['is_active', 'is_email_confirmed'])

    def get_is_active(self):
        if self.created_at + timezone.timedelta(days=1) > timezone.now():
            return True
        return self.is_active
