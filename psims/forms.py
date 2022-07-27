from django.db.models.fields import CharField, IntegerField
from django.forms import widgets
from psims.widgets import CropWidget, DatepickerWidget, PlantingDatepickerWidget,MapPickerWidget,IrrigationWidget
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db.utils import OperationalError
from .models import *
from phonenumber_field.formfields import PhoneNumberField

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))


class SignUpForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        ))
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "First Name",
                "class": "form-control"
            }
        ))      
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Last Name",
                "class": "form-control"
            }
        ))   
    company = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Company",
                "class": "form-control"
            }
        ))      
    
    title = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Title",
                "class": "form-control"
            }
        ), required=False)      



    phone_number = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Phone Number ex. +3749855032",
                "class": "form-control"
            }
        ), required=False)  
               
    crops_regions = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'label': 'crops_regions',
                "placeholder": "Crops/Regions of interest",
                "class": "form-control"
            }
        ), required=False)  
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password check",
                "class": "form-control"
            }
        ))


        
    class Meta:
        model = Profile
        fields = ( 'username', 'email', 'first_name', 'password1', 'password2', 'company', 'phone_number', 'title', 'crops_regions')


def objects_to_choices(objects, value_property, name_property=None):
    choices = list()
    try:
        for obj in objects:
            value = getattr(obj, value_property)
            if name_property:
                name = getattr(obj, name_property)
                choices.append([value, name])
            else:
                choices.append([value, value])
    except OperationalError:
        pass
    return choices


class CropNameForm(forms.ModelForm):
    class Meta:
        model = Crop
        fields = ("name", )

class CropForm(forms.ModelForm):
    class Meta:
        model = Crop
        fields = "__all__"
        widgets = {'name': forms.HiddenInput,
                    'active':forms.HiddenInput}
                    
    crops = Crop.objects.filter(active=True).order_by('name')

    crop = forms.ChoiceField(choices=objects_to_choices(crops, "name"), widget=CropWidget)



class WeatherForm(forms.Form):
    weather_objs = Weather.objects.all()
    weather = forms.ChoiceField(choices=objects_to_choices(weather_objs, "name", "name"),
                                label="Weather Data")


class FertilizationForm(forms.ModelForm):
    class Meta:
        model = FertilizationParameters
        fields = "__all__"
        widgets = {'fertilizer_date': DatepickerWidget}
    
    methods = FertilizerMethod.objects.all()
    feacd = forms.ChoiceField(choices=objects_to_choices(methods, "name", "name_long"),
                              label="Fertilizer method")

    types = FertilizerType.objects.all()
    fecd = forms.ChoiceField(choices=objects_to_choices(types, "name", "name_long"),
                             label="Fertilizer type")




class TillageForm(forms.ModelForm):
    class Meta:
        model = TillageParameters
        fields = "__all__"
        widgets = {'tiimp': forms.HiddenInput()}

    implements = TillageImplement.objects.all()
    tiimp = forms.ChoiceField(choices=objects_to_choices(implements, "name", "name_long"),
                              label="Tillage implement")


class CornForm(forms.ModelForm):
    class Meta:
        model = CornParameters
        fields = "__all__"


# class IrrigationForm(forms.ModelForm):
#     methods = IrrigationMethod.objects.all()
#     iame = forms.ChoiceField(choices=objects_to_choices(methods, "name", "name_long"),
#                              label="Irrigation Method")

#     class Meta:
#         model = IrrigationParameters
#         fields = "__all__"
#         widgets = {'irrig':IrrigationWidget}

class PlantingForm(forms.ModelForm):
    add_planting_dates = forms.CharField(max_length=300, required=False)
    methods = IrrigationMethod.objects.all()
    iame = forms.ChoiceField(choices=objects_to_choices(methods, "name", "name_long"),
                             label="Irrigation Method")
    class Meta:
        model = PlantingParameters
        fields = "__all__"
        widgets = {'planting_date': PlantingDatepickerWidget, 'irrig':IrrigationWidget}



class SoybeanForm(forms.ModelForm):
    class Meta:
        model = SoybeanParameters
        fields = "__all__"

class HempForm(forms.ModelForm):
    class Meta:
        model = HempParameters
        fields = "__all__"

class SpringWheatForm(forms.ModelForm):
    class Meta:
        model = SpringWheatParameters
        fields = "__all__"


class WinterWheatForm(forms.ModelForm):
    class Meta:
        model = WinterWheatParameters
        fields = "__all__"


class SugarcaneForm(forms.ModelForm):
    class Meta:
        model = SugarcaneParameters
        fields = "__all__"


class CottonForm(forms.ModelForm):
    class Meta:
        model = CottonParameters
        fields = "__all__"


class RiceForm(forms.ModelForm):
    class Meta:
        model = RiceParameters
        fields = "__all__"


class BarleyForm(forms.ModelForm):
    class Meta:
        model = BarleyParameters
        fields = "__all__"


class CanolaForm(forms.ModelForm):
    class Meta:
        model = CanolaParameters
        fields = "__all__"


class SorghumForm(forms.ModelForm):
    class Meta:
        model = SorghumParameters
        fields = "__all__"


class ChickpeaForm(forms.ModelForm):
    class Meta:
        model = ChickpeaParameters
        fields = "__all__"


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = "__all__"
        exclude = ('out',)
        widgets = {'latitude': MapPickerWidget, 'longitude': MapPickerWidget}


class CassavaForm(forms.ModelForm):
    class Meta:
        model = CassavaParameters
        fields = "__all__"


class PricingForm(forms.ModelForm):
    class Meta:
        model = Pricing
        fields = "__all__"

class WeightedIndexForm(forms.Form):
    weighted_index = IntegerField(help_text='Please enter the weighted index.')
    ids = IntegerField()
    weighted_name = CharField(max_length=100)

class CsvDataForm(forms.Form):
    checkbox_index = IntegerField()

class CombineForm(forms.Form):
    combine_name = IntegerField()

class UserForm(forms.Form):
    user_name = CharField(max_length=100)
    user_email = CharField(max_length=100) 

class DeleteForm(forms.Form):
    delete_index = IntegerField()

class ExportLiveForm(forms.Form):
    export_ids = IntegerField()

class ExportInputForm(forms.Form):
    export_input = IntegerField()

class EditForm(forms.Form):
    username = CharField(max_length=100)
    useremail = CharField(max_length=100)
    first_name = CharField(max_length=100)
    last_name = CharField(max_length=100)
    company = CharField(max_length=180)
    title = CharField(max_length=100)
    phone_number = CharField(max_length=60)
    crops_regions = CharField(max_length=100)