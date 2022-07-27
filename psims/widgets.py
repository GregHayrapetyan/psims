from django import forms
from django.forms.utils import flatatt
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


class PlantingDatepickerWidget(forms.TextInput):
    def render(self, name,  value,  attrs=None, renderer=None):
        super().render(name, value, attrs)
        return mark_safe(render_to_string('widgets/datepicker_planting_date.html', {
            'name': name,
            'value': value or "",

        }))

class DatepickerWidget(forms.TextInput):
    def render(self, name,  value,  attrs=None, renderer=None):
        super().render(name, value, attrs)
        return mark_safe(render_to_string('widgets/datepicker.html', {
            'name': name,
            'value': value or "",

        }))

class MapPickerWidget(forms.TextInput):
    def render(self, name, value, attrs=None, renderer=None):
        super().render(name, value, attrs)
        return mark_safe(render_to_string('widgets/map-picker.html', {
            'name': name,
            'value': value or "",
        }))

class CropWidget(forms.Textarea):
    def render(self, name, value, attrs=None, renderer=None):
        super().render(name, value, attrs)
        return mark_safe(render_to_string('widgets/Crops.html', {
            'name': name,
            'value': value or "",
        }))

class IrrigationWidget(forms.Textarea):
    def render(self, name, value, attrs=None, renderer=None):
        super().render(name, value, attrs)
        return mark_safe(render_to_string('widgets/irrigation.html', {
            'name': name,
            'value': value or "",
        }))