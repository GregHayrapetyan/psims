from decimal import Context
import json
from typing import FrozenSet
import xlwt
import re
import copy
import threading
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseForbidden, HttpResponse, response
from django.urls import reverse
from django.http.response import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.template import loader
from django import template
from django.views import View
from formtools.wizard.views import SessionWizardView, StepsHelper
from .forms import *
from statistics import mean, pstdev
from .tasks import create_psims
from django.views.decorators.csrf import csrf_exempt
from django.utils.datastructures import MultiValueDictKeyError
from django.core.exceptions import ObjectDoesNotExist, RequestAborted, SuspiciousOperation, ValidationError
import csv
import pandas
import itertools
from datetime import datetime
from django.views.generic import TemplateView
from django.db.models.functions import ExtractWeek, ExtractYear, Extract
from django.db.models import Sum, Count
from datetime import datetime, timedelta, date
import logging
from decimal import *
import stripe
from django.conf import settings
from django.core.mail import send_mail
from django.urls.exceptions import NoReverseMatch
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.views import LogoutView
from psims.planting_hint import planting_hint
from formtools.wizard.forms import ManagementForm
from django.db.models.signals import post_save
from django.dispatch import receiver
import base64
from random import randint
from psims_web_project.celery import app
import redis
from .utils import export_results


def login_view(request):
    form = LoginForm(request.POST or None)
    
    msg = None
    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username").lower()
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})

@login_required
def logout_view(request):
    logout(request)
    return redirect(reverse('login'))


def register_user(request):
    msg = None
    access_msg = None
    success = False
    exist = None
    is_match = False
    if request.method == "POST":

        form = SignUpForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if User.objects.filter(username=data['username']).exists():
                exist = True
                
            else:
                if data['password1'] != data['password2']:
                    
                    is_match = False

                else:
                    is_match = True
                    exist = False
                    user = User.objects.create_user(username = data['username'].lower(),
                                                    email = data['email'],
                                                    first_name = data['first_name'],
                                                    last_name = data['last_name'],
                                                    password = data['password1'])
                    user.is_active = False
                    user.save()
                    print(user.username)
                    profile = Profile.objects.create(user=user, company = data['company'], 
                        phone_number= data['phone_number'], title= data['title'],  
                        crops_regions = data['crops_regions'])
                    profile.save()
                    print(profile.user)
            if exist:
                success = False
                msg = 'Username exist'
            else:
                if is_match:
                    success = True
                    mail_subject = 'Activate your account.'
                    current_site = get_current_site(request)
                    message = render_to_string('acc_active_email.html', {
                        'user': user,
                        'domain': current_site.domain,
                        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                        'token':account_activation_token.make_token(user),
                    })
                    to_email = form.cleaned_data.get('email')
                    email = EmailMessage(
                                mail_subject, message, to=[to_email]
                    )
                    email.send()
                    access_msg = 'Please confirm your email address to complete the registration'
                else:
                    success = False
                    msg = 'Passwords should match.'


        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, 'access_msg':access_msg, "msg": msg, 'exist':exist, "success": success})

@login_required
def choice_card(request):
    cards = Card.objects.all()
    card_title = CardTitle.objects.all()
    return render(request, 'cards.html', {'cards':cards, 'card_title':card_title})


def activate(request, uidb64, token):
  
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        print(uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        mail_subject = 'Activate account.'
        current_site = get_current_site(request)
        message = render_to_string('final_acc_active_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':account_activation_token.make_token(user),
        })
        to_email = 'info@praedictus.com'
        email = EmailMessage(
                    mail_subject, message, to=[to_email]
        )
        email.send()

        access_msg = 'Thank you for your email confirmation. Please wait for account activation.'
        # return redirect('home')
        return render(request, "accounts/register.html", {'access_msg':access_msg, 'exist':False, "success": True})
    else:
        msg = '<p style="color: rgb(254, 89, 86); font-size: 17px; margin-bottom:0px;"> Activation link is invalid! </p>'
        return render(request, "accounts/register.html", {"msg": msg, 'exist':False, "success": True})

def final_activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        print(uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        access_msg = 'User account is activated'
        return render(request, "accounts/register.html", {'access_msg':access_msg, 'exist':False, "success": True})
    else:
        msg = '<p style="color: rgb(254, 89, 86); font-size: 17px; margin-bottom:0px;"> Activation link is invalid! </p>'
        return render(request, "accounts/register.html", {"msg": msg, 'exist':False, "success": True})




class FormWizardView(SessionWizardView):
    user = None
    template_name = "psims/wizard.html"
    form_list = [CropForm, LocationForm, PlantingForm,  FertilizationForm, CornForm]


    def get_context_data(self, form, **kwargs):
        context = super(FormWizardView, self).get_context_data(form=form, **kwargs)

        if self.storage.current_step == "2":
            if self.storage.get_step_data('2') != None:
                
                context.update({'plplp': self.storage.get_step_data('2').get('2-plplp', 5)})
                context.update({'plpop': self.storage.get_step_data('2').get('2-plpop', 5)})
                context.update({'plpoe': self.storage.get_step_data('2').get('2-plpoe', 5)})
            
        if self.storage.current_step == "4":
            # "''3-plpop': ['5.0'], '3-plpoe': ['5.0']}'"
            func_planting_date = planting_hint(self.storage.get_step_data('0').get('0-crop', 'Default'), self.storage.get_step_data('1').get('1-latitude', 'Default'), self.storage.get_step_data('1').get('1-longitude', 'Default'))
            context.update({'crop': self.storage.get_step_data('0').get('0-crop', 'Default')})
            context.update({'planting_date': self.storage.get_step_data('2').get('2-planting_date', 5), 'plpop':self.storage.get_step_data('2').get('2-planting_date', 5)})
            context.update({'func_planting_date': func_planting_date})
        if self.storage.current_step == "3":
            # "''3-plpop': ['5.0'], '3-plpoe': ['5.0']}'"
            context.update({'planting_date': self.storage.get_step_data('2').get('2-planting_date', 5)})
            context.update({'add_planting_dates': self.storage.get_step_data('2').get('2-add_planting_dates', 5)})

        if self.storage.current_step =="2":
            func_planting_date = planting_hint(self.storage.get_step_data('0').get('0-crop', 'Default'), self.storage.get_step_data('1').get('1-latitude', 'Default'), self.storage.get_step_data('1').get('1-longitude', 'Default'))
            context.update({'crop': self.storage.get_step_data('0').get('0-crop', 'Default')})
            context.update({'func_planting_date': func_planting_date})

        
        return context


    def post(self, *args, **kwargs):
        if self.steps.current == "3" and self.request.POST.get('seed', False) == False and self.request.POST.get('wizard_goto_step', False) != '2':
            self.storage.current_step = '4'
            post = self.request.POST.copy()
            prev_data = self.get_cleaned_data_for_step('0')
            crop = str(prev_data['crop'])
            x = CornForm(None)
            if crop == "Corn":
                x = CornForm()
            elif crop == "Barley":
                x = BarleyForm()
            elif crop == "Canola":
                x = CanolaForm()
            elif crop == "Chickpea":
                x = ChickpeaForm()
            elif crop == "Cotton":
                x = CottonForm()
            elif crop == "Hemp":
                x = HempForm()
            elif crop == "Rice":
                x = RiceForm()
            elif crop == "Sorghum":
                x = SorghumForm()
            elif crop == "Soybean":
                x = SoybeanForm()
            elif crop == "Spring Wheat":
                x = SpringWheatForm()
            elif crop == "Sugarcane":
                x = SugarcaneForm()
            elif crop == "Winter Wheat":
                x = WinterWheatForm()
            
            dicta = {}
            for k,v in x.base_fields.items():
                dicta[k] = v.initial
            if crop == "Corn":
                x = CornForm(dicta)
            elif crop == "Barley":
                x = BarleyForm(dicta)
            elif crop == "Canola":
                x = CanolaForm(dicta)
            elif crop == "Chickpea":
                x = ChickpeaForm(dicta)
            elif crop == "Cotton":
                x = CottonForm(dicta)
            elif crop == "Hemp":
                x = HempForm(dicta)
            elif crop == "Rice":
                x = RiceForm(dicta)
            elif crop == "Sorghum":
                x = SorghumForm(dicta)
            elif crop == "Soybean":
                x = SoybeanForm(dicta)
            elif crop == "Spring Wheat":
                x = SpringWheatForm(dicta)
            elif crop == "Sugarcane":
                x = SugarcaneForm(dicta)
            elif crop == "Winter Wheat":
                x = WinterWheatForm(dicta)
            # add rest corns 
            z = self.storage.get_step_data("1")
            z.update(dicta)
            self.storage.set_step_data("3",post)
            self.storage.set_step_data("4",z)
            self.storage._set_current_step("4")
            
            
            # self.steps = StepsHelper(self)
            # self.form_list.pop('4')
            # post.update({'wizard_goto_step':False,'form_wizard_view-current_step':"4"})
            self.request.POST = post
            
        if self.steps.current == "4" and self.storage.get_step_data('3').get('seed', False) == False and self.request.POST.get('wizard_goto_step', False) != '3':
            # form = self.get_form(data=dicta, files=self.request.FILES)
            form_class = self.form_list["4"]
            step  = "4"
            kwargs = self.get_form_kwargs(step)
            kwargs.update({
                'data': dicta,
                'prefix': self.get_form_prefix(step, form_class),
                'initial': self.get_form_initial(step),
            })
            if issubclass(form_class, (forms.ModelForm, forms.models.BaseInlineFormSet)):
                # If the form is based on ModelForm or InlineFormSet,
                # add instance if available and not previously set.
                kwargs.setdefault('instance', self.get_form_instance(step))
            elif issubclass(form_class, forms.models.BaseModelFormSet):
                # If the form is based on ModelFormSet, add queryset if available
                # and not previous set.
                kwargs.setdefault('queryset', self.get_form_instance(step))
            return self.render_done(form_class, **kwargs)
        
        return super(FormWizardView, self).post(self, *args, **kwargs)

    def get_form(self, step=None, data=None, files=None):
        if step is None:
            step = self.steps.current

        if step == '4':
            prev_data = self.get_cleaned_data_for_step('0')
            crop = str(prev_data['crop'])
            if crop == "Corn":
                return CornForm(data)
            elif crop == "Cotton":
                return CottonForm(data)
            elif crop == "Soybean":
                return SoybeanForm(data)
            elif crop == "Sugarcane":
                return SugarcaneForm(data)
            elif crop == "Spring Wheat":
                return SpringWheatForm(data)
            elif crop == "Winter Wheat":
                return WinterWheatForm(data)
            elif crop == "Rice":
                return RiceForm(data)
            elif crop == "Barley":
                return BarleyForm(data)
            elif crop == "Canola":
                return CanolaForm(data)
            elif crop == "Sorghum":
                return SorghumForm(data)
            elif crop == "Chickpea":
                return ChickpeaForm(data)
            elif crop == "Cassava":
                return CassavaForm(data)
            elif crop == "Hemp":
                return HempForm(data)
        if not self.user:
            self.user = self.request.user
        return super(FormWizardView, self).get_form(step, data, files)


    def done(self, form_list, form_dict=None,  **kwargs):
        out_dict = dict()
        long_names = dict()
        keys=[]
        for form in form_list:
            out_dict = {**out_dict, **form.cleaned_data}
            for key, value in form.cleaned_data.items():
                try:
                    if  hasattr(form.instance._meta.get_field(key) ,'name_long'):
                        long_names[form.instance._meta.get_field(key).name_long]= value
                    else:
                        if value != 'unnamed_crop' and key!='active':
                            long_names[key] = value
                except:
                    long_names[key]=value

        last_step = copy.deepcopy(out_dict)
        # location
        loc = self.storage.get_step_data('1')
        location_markers_list = []
        markers_names_list = []
        if loc['1-multy_markers'] and loc['1-location_names']:
            location_markers_list = json.loads(loc['1-multy_markers'])
            markers_names_list = json.loads(loc['1-location_names'])
        else:
            location_markers_list.append([float(loc['1-latitude']), float(loc['1-longitude'])])
            markers_names_list.append(loc['1-name'])
        # crop
        cr = self.storage.get_step_data('0')
        crop = Crop.objects.filter(name = cr['0-crop'])[0]
        try:
            func_planting_date = planting_hint(cr['0-crop'], loc['1-latitude'], loc['1-longitude'])
        except Exception as e:
            raise e
        # Planting date
        planting_dates_list = []
        planting_date = self.storage.get_step_data('2')
        print(planting_date)
        add_planting_dates = planting_date['2-add_planting_dates']
        pd = PlantingParameters()
        pd.planting_date = planting_date['2-planting_date']
        pd.plplp = planting_date['2-plplp']
        pd.pldp = planting_date['2-pldp']
        pd.plrs = planting_date['2-plrs'] 
        pd.plpop = planting_date['2-plpop']
        pd.plpoe = planting_date['2-plpoe']
        if planting_date['2-add_planting_dates']:
            planting_dates_list = [int(i) for i in add_planting_dates.split(',')]
            planting_dates_list.insert(0, int(planting_date['2-planting_date']))
        else:
            planting_dates_list.insert(0, int(planting_date['2-planting_date']))

        # irrigation_parameters

        # fertilizer_param
        fd = self.storage.get_step_data('3')
        fertilizer_param = FertilizationParameters.objects.create(fertilizer_date = fd['3-fertilizer_date'],
        fedep = fd['3-fedep'], feamn = fd['3-feamn'])
        fertilizer_param.save()
        # weather
        # weather_name = 'ERA5'
        is_era = True
        crop_name = cr['0-crop']
        location_name = loc['1-name']
        user_id = self.user.id
        crop_id = crop.id
        fertilizer_param_id = fertilizer_param.id
        is_live = False
        is_open = False
        parent_id = 0
        # out_dict['weather'] = weather_name
        num = randint(1, 999999)
        message = str(num)
        message_bytes = message.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        proccess_id = base64_bytes.decode('ascii')
        r = redis.Redis()
        count = len(planting_dates_list)*len(location_markers_list)
        r.mset({"proccess_id":proccess_id, "count":count})
        for j in planting_dates_list:
            pd = PlantingParameters.objects.create(planting_date = j, 
                plplp = planting_date['2-plplp'],
                pldp = planting_date['2-pldp'], plrs = planting_date['2-plrs'], 
                plpop = planting_date['2-plpop'], plpoe = planting_date['2-plpoe'])
            try:
                if planting_date['2-irrig'] == True:
                    pd.irrig = True
            except MultiValueDictKeyError:
                pd.irrig = False
            pd.iame = planting_date['2-iame']
            pd.save()
            pd_id_changed = pd.id
            out_dict['planting_date'] = j
            iter_count = len(location_markers_list)
            for i in range(iter_count):
                location = Location.objects.create(name = markers_names_list[i], 
                latitude = location_markers_list[i][0], longitude = location_markers_list[i][1], polygon_data =  loc['1-polygon_data'])
                location.save()
                location_id = location.id
                out_dict['name'] = markers_names_list[i]
                out_dict['latitude'] = location_markers_list[i][0]
                out_dict['longitude'] = location_markers_list[i][1]
                t = create_psims.delay(str(proccess_id), out_dict, user_id, location_id, crop_id, pd_id_changed, fertilizer_param_id, 
                last_step, is_era, is_live, parent_id, long_names, is_open)
        print(t.task_id) 
        return render(self.request, "psims/wizard.html", {'success': True, 
        'crop_name': crop_name, 'location_name': location_name, 
        'planting_date':planting_date['2-planting_date'], 'cr':cr, 'fertilizer_date':fd['3-fertilizer_date']
        })


@receiver(post_save, sender=PsimsOutput)
def detect(sender, instance, created, **kwargs):
    if created:
        r = redis.Redis()
        byte_proc_id = r.get("proccess_id")
        proc_id = byte_proc_id.decode('latin1')
        byte_count = r.get("count")
        count = byte_count.decode('latin1')
        objs = PsimsOutput.objects.filter(proccess_id=proc_id)
        print(count, 'count')
        print(objs.count(), 'obj_count')
        if objs.count() == int(count):
            print('mtav')
            export_results(objs)


@login_required
def end_wizard_view(request, username):
    if request.user.username != username:
        return HttpResponseForbidden()
    try:
        if request.method == 'GET' and 'parent' in request.GET:
            parent = request.GET['parent']
            job = PsimsOutput.objects.get(id=int(parent))

            out_dict = job.last_step_json
            is_live = True
            parent_id = job.id
            is_open = True
            create_psims.delay(out_dict, job.owner.id, job.location.id,
                job.crop.id, job.planting_day.id, job.fertilizer_day.id,
                job.last_step_json, job.is_era, is_live, parent_id, job.long_names, is_open)
            job.is_parent = True
            job.save()
        else:
            parent = 0

    except PsimsOutput.DoesNotExist:
        raise Http404("No results matched")
    return render(request, 'psims/wizard_view.html', {'success':True, 'parent_id':parent_id})

def export_inputs_function(export):
    values_list = []
    col_name = []
    wb = xlwt.Workbook()
    for j in export:
        long_names = j.long_names
        
        for key, value in long_names.items():
            col_name.append(key)
            values_list.append(value)
        worksheet_name = j.created_at.strftime("%Y_%m_%d_%H_%M")
        ws = wb.add_sheet("Inputs_"+worksheet_name)
        
        al = xlwt.Alignment()
        font_style1 = xlwt.XFStyle()
        font_style1.font.bold = True
        font_style1.alignment.wrap = 1
        font_style2 = xlwt.XFStyle()
        font_style2.font.bold = False
        font_style2.alignment.wrap = 1
        font_style2.align = al
        font_style2.alignment.horz = al.HORZ_LEFT 
        for i in range(len(col_name)):
            ws.write(i, 0, col_name[i].title(), font_style1)
            ws.col(i).height_mismatch = True
            ws.col(i).width = 330*20
        for i in range(len(values_list)):
            ws.write(i, 1, values_list[i], font_style2)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=User_inputs.xls'
    wb.save(response)
    return response


@login_required
def result(request, username, id):
    if request.user.username != username:
        return HttpResponseForbidden()
    try:
        result=[]
        result = PsimsOutput.objects.get(id=id, owner=request.user.id)
        loaded_json = json.loads(result.json)
        location_name = result.location.name
        crop_name = result.crop.name
        is_live = result.is_live
        years = loaded_json['YEAR']
        yields = loaded_json['HWAM']
        year_list = []
        for key in years:
            year_list.insert(int(key), str(years[key]))
        yield_list = []
        for key in yields:
            yield_list.insert(int(key), yields[key])
        avg = mean(yield_list)
        round_avg = round(avg, 2)
        yield_count = len(yield_list)
        count = len(year_list)
        if count>yield_count:
            num = count - yield_count
            count -= num
            year_list = year_list[:-num]
        # Calculate google graph data - kg/hectar
        csv_data = []
        for i in range(count):
            csv_data.append([year_list[i], yield_list[i]])
        # Calculate google graph data  bushels/acre
        csv_data_bushels = []
        for i in range(count):
            csv_data_bushels.append(
                [year_list[i], round(yield_list[i] * 0.0149, 2)])
        # Calculate yields and high and lows
        last_yield = str(yield_list[count - 1])
        penultimate_yield = str(yield_list[count - 2])
        last_year = str(year_list[count - 1])
        penultimate_year = str(year_list[count - 2])

        average_yield = str(round_avg)
        open_result = None
        if result.id:
            result.is_open = True
            result.save()
            open_result = result.is_open
        is_weigted_index = result.is_weighted_index    
        last_year_bushels = str(round((yield_list[count - 1]) * 0.0149, 2))
        penultimate_year_bushels = str(round((yield_list[count - 2]) * 0.0149, 2))
        average_yield_bushels = str(round(round_avg * 0.0149, 2))
        high_yield_value = max(yield_list)
        low_yield_value = min(yield_list)
        high = str(high_yield_value)
        low = str(low_yield_value)
        high_bushels = str(round(high_yield_value * 0.0149, 2))
        low_bushels = str(round(low_yield_value * 0.0149, 2))
        high_year_index = yield_list.index(high_yield_value)
        low_year_index = yield_list.index(low_yield_value)
        high_year = str(year_list[high_year_index])
        
        low_year = str(year_list[low_year_index])
        total_yields = 0
        for i in range(count):
            total_yields = total_yields + yield_list[i]
        if 0 != total_yields:
            percent_of_last_year = round(
                ((yield_list[count - 1] / total_yields) * 1000), 2)
        else:
            percent_of_last_year = 0
        # Calculate morris graph data - kg/hectare
        morris_chart_data = []
        for i in range(count):
            element = {'y': year_list[i], 'a': yield_list[i], 'b': round_avg}
            morris_chart_data.append(element)
        # Calculate morris graph data - bushels/acre
        morris_chart_data_bushels = []
        for i in range(count):
            element = {'y': year_list[i], 'a': round(
                yield_list[i] * 0.0149, 2), 'b': round(round_avg * 0.0149, 2)}
            morris_chart_data_bushels.append(element)
        results = PsimsOutput.objects.filter(is_live=True, parent=id).order_by('-id')
        export_form = ExportLiveForm()
        export_inputs = ExportInputForm()
        if request.method == "POST":
            export_form = ExportLiveForm(request.POST)
            export_inputs = ExportInputForm(request.POST)
            if export_form.is_valid():
                if 'export_ids' in request.POST:
                    export_ids = request.POST["export_ids"]
                    export = list()
                    results = PsimsOutput.objects.filter(is_live=True, parent=id).order_by('-id')
                    wb = xlwt.Workbook()
                    ws = wb.add_sheet("Inputs")
                    al = xlwt.Alignment()
                    font_style2 = xlwt.XFStyle()
                    font_style2.font.bold = False
                    font_style2.alignment.wrap = 1
                    font_style2.align = al
                    font_style2.alignment.horz = al.HORZ_LEFT 
                    ws.col(0).height_mismatch = True
                    ws.col(0).width = 330*20
                    ws.col(1).height_mismatch = True
                    ws.col(1).width = 330*20
                    ws.write(0, 0, 'Live Yield as', font_style2)
                    ws.write(0, 1, 'Last Year Yield', font_style2)
                    ws.write(1, 0, str(result), font_style2)
                    ws.write(1, 1, str(last_yield), font_style2)
                    for i in range(len(results)):
                        ws.col(i+2).height_mismatch = True
                        ws.col(i+2).width = 330*20
                        ws.write(i+2, 0, str(results[i]), font_style2)
                        ws.write(i+2, 1, str(results[i].last_yield), font_style2)
                    response = HttpResponse(content_type='text/csv')
                    response['Content-Disposition'] = 'attachment; filename=User_inputs.xls'
                    wb.save(response)
                    return response
                    return HttpResponseRedirect(reverse("result", kwargs={"username":username, "id":id}))
            if export_inputs.is_valid():
                if 'export_input' in request.POST:
                    export_input = request.POST["export_input"]
                    export = list()
                    json_object = PsimsOutput.objects.get(id=id)
                    export.append(json_object)
                    response = export_inputs_function(export)
                    return response
                    return HttpResponseRedirect(reverse("result", kwargs={"username":username, "id":id}))
        
    except PsimsOutput.DoesNotExist:
        raise Http404("No results matched")
    return render(request, 'psims/result.html',
                  {'csv_data': csv_data,
                   'csv_data_bushels': csv_data_bushels,
                   'morris_data': morris_chart_data,
                   'morris_data_bushels': morris_chart_data_bushels,
                   'last_year': last_year,
                   'penultimate_year': penultimate_year,
                   'penultimate_yield' : penultimate_yield,
                   'penultimate_year_bushels':penultimate_year_bushels,
                   'last_yield': last_yield,
                   'last_yield_bushels': last_year_bushels,
                   'percent_last_year': percent_of_last_year,
                   'average_yield': average_yield,
                   'average_yield_bushels': average_yield_bushels,
                   'count': count,
                   'high': high,
                   'low': low,
                   'high_bushels': high_bushels,
                   'low_bushels': low_bushels,
                   'high_year': high_year,
                   'low_year': low_year,
                   'user_name': username,
                   'user_id': id,
                   'location_name': location_name,
                   'crop_name': crop_name,
                   'is_weigted_index':is_weigted_index,
                   'is_live':is_live,
                   'result':result,
                   'results':results,
                   'export_form':export_form,
                   'export_inputs': export_inputs
                   })


@login_required
def risk(request, username, id):
    if request.user.username != username:
        return HttpResponseForbidden()
    try:
        result = PsimsOutput.objects.get(id=id, owner=request.user)
        loaded_json = json.loads(result.json)
        years = loaded_json['YEAR']
        yields = loaded_json['HWAM']
        year_list = []
        is_weigted_index = result.is_weighted_index   
        for key in years:
            year_list.insert(int(key), str(years[key]))
        yield_list = []
        yield_list_bushels = []
        for key in yields:
            yield_list.insert(int(key), yields[key])
            yield_list_bushels.insert(int(key), round(yields[key] * 0.0149, 2))
        avg = mean(yield_list)
        avg_bushels = round(avg * 0.0149, 2)
        round_avg = round(avg, 2)
        average_yield = str(round_avg)
        yield_count = len(yield_list)
        count = len(year_list)
        if count>yield_count:
            num = count - yield_count
            count -= num
            year_list = year_list[:-num]

        # Calculate morris graph data - kg/hectare
        morris_chart_data = []
        for i in range(count):
            element = {'y': year_list[i], 'a': yield_list[i], 'b': round_avg}
            morris_chart_data.append(element)
        # Calculate morris graph data - bushels/acre
        morris_chart_data_bushels = []
        for i in range(count):
            element = {'y': year_list[i], 'a': round(
                yield_list[i] * 0.0149, 2), 'b': round(round_avg * 0.0149, 2)}
            morris_chart_data_bushels.append(element)
    except PsimsOutput.DoesNotExist:
        raise Http404("No results matched")
    return render(request, 'psims/risk-transfer.html',
                  {'morris_data': morris_chart_data,
                   'morris_data_bushels': morris_chart_data_bushels,
                   'average_yield': average_yield,
                   'average_yield_bushels': avg_bushels,
                   'year_list': year_list,
                   'yield_list': yield_list,
                   'yield_list_bushels': yield_list_bushels,
                   'count': count,
                   'user_name': username,
                   'user_id': id,
                   'is_weigted_index':is_weigted_index})


@csrf_exempt
@login_required
def results_list(request, username):
    if request.user.username != username:
        return HttpResponseForbidden()
    try:
        weighted_index_form = WeightedIndexForm()
        csv_data_form = CsvDataForm()
        delete_form = DeleteForm()
        jsons = []
        col_name = []
        weight_index_dict = {}
        results = PsimsOutput.objects.filter(owner=request.user).order_by('-id')
        new= PsimsOutput.objects.filter( owner=request.user)
        if request.method == 'POST':
            weighted_index_form = WeightedIndexForm(request.POST)
            csv_data_form = CsvDataForm(request.POST)
            delete_form = DeleteForm(request.POST)
            combine_form = CombineForm(request.POST)
            if "checkbox_index" in request.POST:
                if csv_data_form.is_valid():
                    checkbox_index_string = request.POST["checkbox_index"]
                    checkbox_index = list(map(int, checkbox_index_string.split(',')))
                    json_year_list =[]
                    json_yield_list =[]
                    result = []
                    for i in checkbox_index:
                        json_object = PsimsOutput.objects.get(id=i)
                        loaded_json = json.loads(json_object.json)
                        json_year = loaded_json['YEAR']
                        json_yield = loaded_json['HWAM']
                        for key in loaded_json:
                            col_name.append(key)
                        year_list = list(json_year.values())
                        yield_list = list(json_yield.values())
                        yield_count = len(yield_list)
                        count = len(year_list)
                        if count>yield_count:
                            num = count - yield_count
                            count -= num
                            year_list = year_list[:-num]
                        json_year_list.append(year_list)
                        json_yield_list.append(yield_list)
                    for i,j in zip(json_year_list, json_yield_list):
                        result.append(i)
                        result.append(j)
                    response = HttpResponse(content_type='text/csv')
                    response['Content-Disposition'] = 'attachment; filename=weighted_index.csv'
                    writer = csv.writer(response)
                    df = pandas.DataFrame((_ for _ in itertools.zip_longest(*result)), columns=col_name)
                    df.to_csv(response, index=False)
                    return response
            if "weighted_index" and "weighted_index" and "weighted_name" in request.POST:
                weight_string = request.POST["weighted_index"]
                weight_id_string = request.POST["ids"]
                weighted_name= request.POST["weighted_name"]
                if weighted_index_form.is_valid():
                    try:
                        weight = list(map(int, weight_string.split(',')))
                        weight_id = list(map(int, weight_id_string.split(',')))
                    except:
                        raise ValueError    
                    object = []
                    yields_list = []
                    yields_list_new = []
                    finish = []
                    sum_weight = sum(weight)
                    l=0
                    part = []
                    sum_of_multiply = 0
                    for i in weight_id:
                        object.append(PsimsOutput.objects.get(id=i))
                        
                    for i in range(len(object)):
                        loaded_json = json.loads(object[i].json)
                        years = loaded_json['YEAR']
                        json_yields = loaded_json['HWAM']
                        yields_list.append(list(json_yields.values()))

                    for i in yields_list:
                        avg = mean(i)
                        yields_list_new.append([j/avg for j in i])
                    sum_of_values = 0
                    while l !=len(weight):
                        r  = weight[l]/sum_weight
                        part.append(r)
                        l+=1
                    multiply = 1
                    for i in range(len(yields_list_new[0])): # first list items, 40 items
                        for k in range(len(part)):
                            if k == len(part)-1:
                                finish.append(round(sum_of_multiply/100, 2))
                            sum_of_multiply = 0
                            for j in range(len(yields_list_new)): # all lists first elements
                                multiply = round(part[j]*100,2)*round(yields_list_new[j][i]*100,2)
                                sum_of_multiply += multiply
                    weight_index_dict = {}
                    for index,value in enumerate(finish):
                        weight_index_dict[str(index)] = value
                    s1 = {"YEAR":years,'HWAM':weight_index_dict}
                    output = json.dumps(s1)
                    print(output)
                    average = mean(weight_index_dict.values())
                    location = Location.objects.create(name = 'Default', 
                    latitude = 39.43530142067006, longitude = 92.34310605480388)
                    location.save()
                    crop = Crop.objects.create(name = weighted_name)
                    crop.save()
                    out = PsimsOutput.objects.create(json=output, owner=request.user, location=location, crop=crop, 
                    is_weighted_index = True, is_open = False, average_yield=average)
                    out.save()

                    return HttpResponseRedirect(reverse("results", kwargs={"username":username}))
            if 'delete_index' in request.POST:
                if delete_form.is_valid():
                    delete_index_string = request.POST['delete_index']
                    if delete_index_string:
                        delete_index = list(map(int, delete_index_string.split(',')))
                        for i in delete_index:
                            deleted_obj = PsimsOutput.objects.get(id=i)
                            deleted_obj.is_deleted =True
                            deleted_obj.save()
                    else:
                        pass
            if 'combine_name' in request.POST:
                if combine_form.is_valid():
                    combine_string = request.POST['combine_name']
                    if combine_string:
                        combine_index = list(map(int, combine_string.split(',')))
                        wb = xlwt.Workbook()
                        ws = wb.add_sheet("Inputs")
                        al = xlwt.Alignment()
                        font_style1 = xlwt.XFStyle()
                        font_style1.font.bold = True
                        font_style1.alignment.wrap = 1
                        font_style2 = xlwt.XFStyle()
                        font_style2.font.bold = False
                        font_style2.alignment.wrap = 1
                        font_style2.align = al
                        font_style2.alignment.horz = al.HORZ_LEFT 
                        ws.col(0).height_mismatch = True
                        ws.col(0).width = 330*20
                        ws.col(1).height_mismatch = True
                        ws.col(1).width = 330*20
                        ws.write(0, 0, 'RunDateTime', font_style1)
                        ws.write(0, 1, 'Location', font_style1)
                        ws.write(0, 2, 'Crop', font_style1)
                        ws.write(0, 3, 'PlantingDate', font_style1)
                        ws.write(0, 4, 'Lat', font_style1)
                        ws.write(0, 5, 'Lon', font_style1)
                        ws.write(0, 6, 'Year', font_style1)
                        ws.write(0, 7, 'YieldIndex', font_style1)
                        for i in range(len(combine_index)):
                            combine_obj = PsimsOutput.objects.get(id=combine_index[i])
                            ws.write(i+1, 0, str(combine_obj.created_at), font_style2)
                            ws.write(i+1, 1, str(combine_obj.location), font_style2)
                            ws.write(i+1, 2, str(combine_obj.crop), font_style2)
                            ws.write(i+1, 3, str(combine_obj.planting_day.planting_date), font_style2)
                            ws.write(i+1, 4, str(combine_obj.location.latitude), font_style2)
                            ws.write(i+1, 5, str(combine_obj.location.longitude), font_style2)
                            ws.write(i+1, 6, str(combine_obj.last_year), font_style2)
                            ws.write(i+1, 7, str(combine_obj.last_year), font_style2)
                        response = HttpResponse(content_type='text/csv')
                        response['Content-Disposition'] = 'attachment; filename=User_inputs.xls'
                        wb.save(response)
                        return response

    except PsimsOutput.DoesNotExist:
        raise Http404("No results found")
    return render(request, 'psims/results.list.template', {'results': results, 'username': username, 
    'weighted_index_form':weighted_index_form, 'csv_data_form':csv_data_form})


@login_required(login_url="/login/")
def index(request):
    context = {}
    context['segment'] = 'index'
    html_template = loader.get_template('index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1] 
        print(load_template,'kjhgf')
        context['segment'] = load_template
        html_template = loader.get_template(load_template)

        return HttpResponse(html_template.render(context, request))
    except template.TemplateDoesNotExist:
        html_template = loader.get_template('page-404.html')
        return HttpResponse(html_template.render(context, request))
    except:
        html_template = loader.get_template('page-500.html')
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def check_worker_status(request):
    if hasattr(request.user, 'psims_worker'):
        worker = request.user.psims_worker
        if worker and worker.completed_worker_id and not worker.is_seen:
            return JsonResponse({"completed":True,'completed_worker_id': worker.completed_worker_id, 'user':request.user.id})
    return JsonResponse({'completed': False})


# Liv Yield View
# @login_required
# def chart(request, username):
#     if request.user.username != username:
#         return HttpResponseForbidden()
#     try:
#         results = PsimsOutput.objects.filter(owner=request.user)
 
#     except PsimsOutput.DoesNotExist:
#         raise Http404("No results found")
#     return render(request, 'psims/chart.html', {'results': results, 'username': username})

@csrf_exempt
@login_required
def my_account(request):
    try:
        results = PsimsOutput.objects.filter(owner=request.user)
        count = PsimsOutput.objects.filter(owner=request.user, is_deleted = False)
        user = request.user
        reg_form = EditForm(request.POST)
        exist = False
        if request.method == 'POST':
            if reg_form.is_valid():
                username = request.POST['username']
                email = request.POST['email']
                first_name = request.POST['first_name']
                last_name = request.POST['last_name']
                company = request.POST['company']
                title = request.POST['title']
                phone_number = request.POST['phone_number']
                crops_regions = request.POST['crops_regions']
                try:
                    if len(username) == 0:
                        raise ValidationError("WRITE SOMETHING")
                    if user.username != username:
                        if User.objects.filter(username = username).exists():
                            exist = True
                        else:
                            user.username = username
                            user.save()
                    else:
                        user.username = username
                        user.save()
                except NoReverseMatch:
                    raise ValidationError("Write something!")
                user.email = email
                user.first_name = first_name
                user.last_name = last_name
                user.profile.company = company
                user.profile.title = title
                user.profile.phone_number = phone_number
                user.profile.crops_regions = crops_regions
                user.profile.save()
                user.save()

    except PsimsOutput.DoesNotExist:
        raise Http404("No results found")
    return render(request, 'psims/my_account.html', {'results': results, 'username': request.user.username,
     'count':len(count), 'reg_form':reg_form, 'exist':exist})             


stripe.api_key = settings.STRIPE_SECRET_KEY
class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        product_id = self.kwargs["pk"]
        product = Product.objects.get(id=product_id)
        YOUR_DOMAIN = "http://localhost:8000"
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': product.price,
                        'product_data': {
                            'name': product.name
                        },
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                "product_id": product.id
            },
            mode='payment',
            success_url=YOUR_DOMAIN + '/success/',
            cancel_url=YOUR_DOMAIN + '/cancel/',
        )
        return JsonResponse({
            'id': checkout_session.id
        })


class SuccessView(TemplateView):
    template_name = "psims/success.html"



class CancelView(TemplateView):
    template_name = "psims/cancel.html"


class ProductLandingPageView(TemplateView):
    template_name = "psims/landing.html"
    
    def get_context_data(self, **kwargs):
        product = Product.objects.get(name="Test Product")
        context = super(ProductLandingPageView, self).get_context_data(**kwargs)
        context.update({
            "product": product,
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLISHABLE_KEY
        })
        return context


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        customer_email = session["customer_details"]["email"]
        product_id = session["metadata"]["product_id"]

        product = Product.objects.get(id=product_id)

        # TODO - send an email to the customer
        send_mail(
        subject="Here is your product",
        message=f"Thanks for your purchase. The URL is: {product.url}",
        recipient_list=[customer_email],
        from_email="melkon.hovhannisian@gmail.com"
    )
    elif event["type"] == "payment_intent.succeeded":
        intent = event['data']['object']

        stripe_customer_id = intent["customer"]
        stripe_customer = stripe.Customer.retrieve(stripe_customer_id)

        customer_email = stripe_customer['email']
        product_id = intent["metadata"]["product_id"]

        product = Product.objects.get(id=product_id)

        send_mail(
            subject="Here is your product",
            message=f"Thanks for your purchase. The URL is {product.url}",
            recipient_list=[customer_email],
            from_email="melkon.hovhannisian@gmail.com"
        )
    return HttpResponse(status=200)

class StripeIntentView(View):
    def post(self, request, *args, **kwargs):
        try:
            req_json = json.loads(request.body)
            customer = stripe.Customer.create(email=req_json['email'])
            product_id = self.kwargs["pk"]
            product = Product.objects.get(id=product_id)
            intent = stripe.PaymentIntent.create(
                amount=product.price,
                currency='usd',
                customer=customer['id'],
                metadata={
                    "product_id": product.id
                }
            )
            return JsonResponse({
                'clientSecret': intent['client_secret']
            })
        except Exception as e:
            return JsonResponse({ 'error': str(e) })
