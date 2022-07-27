from django.db import reset_queries
from psims.psims import psims
from psims.models import  Location, PsimsOutput, PsimsUser, Crop, PlantingParameters, User, FertilizationParameters, Weather
from django.shortcuts import render
from psims_web_project.celery import app
from statistics import mean, pstdev
import json
import xlwt
from django.http import Http404, HttpResponseForbidden, HttpResponse, response
import redis


@app.task()
def create_psims(proccess_id, out_dict, user_id, location_id, crop_id, pd_id, fertilizer_param_id,
  last_step, is_era, is_live, parent_id, long_names, is_open):
    user = User.objects.get(id = user_id)
    psims_user, is_created = PsimsUser.objects.get_or_create(user=user)
    if not is_created:
        psims_user.completed_worker_id = False
        psims_user.is_seen = False
        psims_user.save()
    json_field = psims(out_dict)
    
    location = Location.objects.get(id=location_id)
    crop = Crop.objects.get(id = crop_id)
    pd = PlantingParameters.objects.get(id=pd_id)
    fertilizer_param = FertilizationParameters.objects.get(id=fertilizer_param_id)
    
    loaded_json = json.loads(json_field)
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
    last_year = str(year_list[count - 1])
    average_yield = str(round_avg)
    output = PsimsOutput(proccess_id=proccess_id, json=json_field, owner=user, location=location, crop=crop, planting_day=pd, fertilizer_day =fertilizer_param, 
    last_step_json= last_step, last_yield=last_yield, last_year=last_year, average_yield=average_yield,
    is_era=is_era, is_live=is_live, parent=parent_id, long_names=long_names, is_open=is_open)
    if hasattr(output, 'json'):
        output.save()
        psims_user.is_seen = False
        psims_user.completed_worker_id = output.id
        psims_user.save()
    else:
        psims_user.is_seen = False
        psims_user.completed_worker_id = "error"
        psims_user.save()
    
