import pandas as pd

from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from localized_fields.admin import LocalizedFieldsAdminMixin

from apps.content.models import School
from apps.location.models import City


class CityForm(forms.ModelForm):
    file = forms.FileField(required=False, help_text="Upload an Excel file to create questions.")

    class Meta:
        model = City
        fields = '__all__'

    def save(self, commit=True):
        city = super().save(commit=False)
        file = self.cleaned_data.get('file')
        if file:
            self.validate_and_process_file(file, city)
        return city

    def validate_and_process_file(self, file, city):
        try:
            df = pd.read_excel(file)
        except Exception as e:
            raise ValidationError(f"Error reading Excel file: {e}")
        self.process_file(df, city)

    def process_file(self, df, exam_subject):
        for _, row in df.iterrows():
            city, created = City.objects.get_or_create(name__ru=row['city'],
                                                       defaults={'name': {'ru': row['city'], 'kk': row['city']}})

            school, created = School.objects.get_or_create(name__ru=row['school_name'],
                                                           defaults={
                                                               'city_id': city.id,
                                                               'name': {'ru': row['school_name'],
                                                                        'kk': row['school_name']}
                                                           })


@admin.register(City)
class CityAdmin(LocalizedFieldsAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'priority')
    form = CityForm
