from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.authentication.services import validate_password_in_forms
from .models import User, UserQuizQuestion, Avatar
from django.contrib.admin.widgets import FilteredSelectMultiple

from ..content.models import Course, Topic


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повторите Пароль', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        validate_password_in_forms(password1, password2)

        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class ChildrenInline(admin.TabularInline):
    model = User
    fields = ('id', 'full_name', 'mobile_phone',)
    readonly_fields = ('id', 'full_name', 'mobile_phone',)
    extra = 0


class UserChangeForm(forms.ModelForm):
    enabled_courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(verbose_name='Курсы', is_stacked=False)
    )
    enabled_topics = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(verbose_name='Темы', is_stacked=False)
    )

    class Meta:
        model = User
        fields = '__all__'

    def init(self, *args, **kwargs):
        super(UserChangeForm, self).init(*args, **kwargs)
        if self.instance.pk:
            self.fields['enabled_courses'].initial = self.instance.enabled_courses.all()
            self.fields['enabled_topics'].initial = self.instance.enabled_topics.all()
        else:
            self.fields['enabled_courses'].initial = []
            self.fields['enabled_topics'].initial = []

    def save(self, commit=True):
        user = super(UserChangeForm, self).save(commit=False)
        if commit:
            user.save()
        user.enabled_courses.set(self.cleaned_data['enabled_courses'])
        user.enabled_topics.set(self.cleaned_data['enabled_topics'])
        self.save_m2m()
        return user


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'mobile_phone', 'role', 'full_name', 'email', 'is_email_confirmed', 'is_staff')
    list_filter = ('is_staff',)
    list_display_links = ('id', 'mobile_phone', 'email', 'is_staff',)
    search_fields = ('email', 'uuid', 'mobile_phone')
    filter_horizontal = ('groups', 'user_permissions', 'enabled_courses', 'enabled_topics')
    add_form = UserCreationForm
    form = UserChangeForm

    ordering = ['-created_at']
    inlines = [ChildrenInline]

    fieldsets = (
        (None, {
            "fields": (
                'uuid',
                'mobile_phone',
                'email',
                'full_name',
                'password',
                'role',
                'is_superuser',
                'is_active',
                'is_staff',
                'enabled_courses',
                'enabled_topics',
                'is_email_confirmed',
                'groups',
                'user_permissions',
                'created_at',
            )
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'role',
                'is_superuser',
                'is_staff',
                'enabled_courses',
                'enabled_topics',
                'groups',
                'user_permissions',
            ),
        }),
    )


admin.site.register(Avatar)
