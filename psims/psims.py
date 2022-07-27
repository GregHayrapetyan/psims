import datetime
import glob
import math
import os
import pandas as pd
import subprocess
import tempfile


def fix_float(f):
    return str(round(f, 1)).rstrip('0').rstrip('.')


def add_pricing_information(csv_path, values):
     from sklearn.linear_model import LinearRegression
     strike = values['strike']
     full_payout = values['full_payout']
     desired_coverage = values['desired_coverage']
     payout = 0
     indicative_rate_online = 0
 
     df = pd.read_csv(csv_path)
     x = df['YEAR'].values.reshape(-1, 1)
     y = df['HWAM'].values.reshape(-1, 1)
     lr = LinearRegression()
     lr.fit(x, y)
     prediction = lr.predict(x)
     percent_of_normal = y / prediction * 100
 
     with open(csv_path, 'w') as output:
         print("YEAR,HWAM,Prediction,% of Normal,Payout", file=output)
         for i,pnorm in enumerate(percent_of_normal):
             pnorm = pnorm[0]
             year = x[i][0]
             hwam = y[i][0]
             current_prediction = prediction[i][0]
             if pnorm > strike:
                 payout = 0
             elif pnorm <= full_payout:
                 payout = 100
             else:
                 payout = (strike - pnorm) / (strike - full_payout) * 100
             indicative_rate_online += payout
             print(year, hwam, fix_float(current_prediction), fix_float(pnorm), fix_float(payout), sep=',', file=output)
    

def latlon_to_grid(lat, lon, delta, padding=4):
    delta = delta / 60.
    latidx = int(math.floor((90. - lat) / delta + 1))
    lonidx = int(math.floor((lon + 180.) / delta + 1))
    lat_tile = str(latidx).zfill(padding)
    lon_tile = str(lonidx).zfill(padding)
    return lat_tile, lon_tile


def run_command(command):
    print(command)
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(result.stdout)
    print(result.stderr)


def template_replace(values, template, new_file):
    template = template.replace(" ", "_")
    template_file = open(template, 'rt')
    template_data = template_file.read()
    for key in values.keys():
        string_to_replace = "{{ " + key + " }}"
        value = str(values[key])
        template_data = template_data.replace(string_to_replace, value)
    template_file.close()
    new_file = open(new_file, "wt")
    new_file.write(template_data)
    new_file.close()

# The below won't run locally - change to something like when you get to this
# def psims(values):
#     sleep 20;
#     cat /path/to/foo.csv




# The below won't run locally - change to something like when you get to this
def psims(values):
    import time
    print('waiting dummy')
    time.sleep(5)
    value = {
        "YEAR": {
            "0": 1979,
            "1": 1980,
            "2": 1981,
            "3": 1982,
            "4": 1983,
            "5": 1984,
            "6": 1985,
            "7": 1986,
            "8": 1987,
            "9": 1988,
            "10": 1989,
            "11": 1990,
            "12": 1991,
            "13": 1992,
            "14": 1993,
            "15": 1994,
            "16": 1995,
            "17": 1996,
            "18": 1997,
            "19": 1998,
            "20": 1999,
            "21": 2000,
            "22": 2001,
            "23": 2002,
            "24": 2003,
            "25": 2004,
            "26": 2005,
            "27": 2006,
            "28": 2007,
            "29": 2008,
            "30": 2009,
            "31": 2010,
            "32": 2011,
            "33": 2012,
            "34": 2013,
            "35": 2014,
            "36": 2015,
            "37": 2016,
            "38": 2017,
            "39": 2018
        },
        "HWAM": {
            "0": 5332,
            "1": 1806,
            "2": 4482,
            "3": 3562,
            "4": 4045,
            "5": 5151,
            "6": 4805,
            "7": 4791,
            "8": 5827,
            "9": 2208,
            "10": 4015,
            "11": 4044,
            "12": 4644,
            "13": 5171,
            "14": 4558,
            "15": 3968,
            "16": 3637,
            "17": 5236,
            "18": 4525,
            "19": 5572,
            "20": 4590,
            "21": 4435,
            "22": 4526,
            "23": 4045,
            "24": 4412,
            "25": 4920,
            "26": 5572,
            "27": 4756,
            "28": 5783,
            "29": 5019,
            "30": 6338,
            "31": 6045,
            "32": 4022,
            "33": 1897,
            "34": 3642,
            "35": 4781,
            "36": 5306,
            "37": 4599,
            "38": 4542,
            "39": 4930
        }
    }
    import json
    return json.dumps(value)



# def psims(values):
#     ref_year = 1979

#     if values['irrig']:
#         values['irrig'] = "A"
#     else:
#         values['irrig'] = "N"

#     # Convert planting_date from doy to yyyymmdd for use in the 'date' field of the planting event
#     new_planting_date = datetime.datetime(ref_year, 1, 1) + datetime.timedelta(int(values['planting_date']) - 1)
#     values['planting_date'] = "%02d%02d%02d" % (new_planting_date.year, new_planting_date.month, new_planting_date.day)

#     psims_root = "/web/psims_web/templates/psims"
#     crop = values['crop']
#     crop_lower = crop.lower().replace(" ", "_")
#     experiment_template = os.path.join(psims_root, "%s.template" % crop.lower())
#     tmp_str = next(tempfile._get_candidate_names())
#     tmp_directory = os.path.join("/web/psims_web/tmp", tmp_str)

#     # Create experiment file
#     os.mkdir(tmp_directory)
#     os.chdir(tmp_directory)
#     new_experiment = os.path.join(tmp_directory, "exp_template.json")
#     template_replace(values, experiment_template, new_experiment)

#     # Copy files to campaign directory on google storage
#     gs_root = "gs://psims_web/scratch"
#     gs_scratch = os.path.join(gs_root, tmp_str)
#     run_command("gsutil cp exp_template.json %s/" % gs_scratch)
#     run_command("gsutil cp %s %s/" % (os.path.join(psims_root, "Campaign.nc4"), gs_scratch))

#     # Run pysims
#     lat = values['latitude']
#     lon = values['longitude']
#     tlatidx, tlonidx = latlon_to_grid(lat, lon, 120)
#     latidx, lonidx = latlon_to_grid(lat, lon, 3)
#     run_command(
#         "source /analysis/bin/setup.sh && /psims/pysims/pysims.py --params "
#         "gs://psims_web/%s/params/3arc.%s.params --campaign %s --tlatidx %s --tlonidx %s --latidx "
#         "%s --lonidx %s --rundir $PWD" % (crop_lower, crop_lower,
#             gs_scratch, tlatidx, tlonidx, latidx, lonidx))

#     # Gather data
#     filename = glob.glob("%s/*/*/Summary.OUT" % tmp_directory)[0]
#     csv_path = "/web/psims_web/static/results/%s" % tmp_str
#     run_command(
#         "source /analysis/bin/setup.sh && /psims/bin/summarize -s %s -v HWAM -y 1979 -o %s" % (
#             filename, csv_path))

#     # Add pricing information, if requested
#     # if values['pricing']:
#     #    add_pricing_information(csv_path, values) 

#     # Create psimsoutput object
#     df = pd.read_csv(csv_path)
#     return df.to_json()
