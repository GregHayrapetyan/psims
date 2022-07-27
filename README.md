## Before you run

Create a python virtual environment. See https://docs.python.org/3/library/venv.html for more information about how to do this. Once your venv is activated, install the requirements by running:
- `pip3 install -r requirements.txt`

The following commands will import some of the reference data you'll need to get started:

- `python manage.py import_model --csv psims/csv/Crop.csv --model Crop`
- `python manage.py import_model --csv psims/csv/FertilizerMethod.csv --model FertilizerMethod`
- `python manage.py import_model --csv psims/csv/FertilizerType.csv --model FertilizerType`
- `python manage.py import_model --csv psims/csv/IrrigationMethod.csv --model IrrigationMethod`
- `python manage.py import_model --csv psims/csv/TillageImplement.csv --model TillageImplement`
- `python manage.py import_model --csv psims/csv/Weather.csv --model Weather`

Create a user account:
- python manage.py createsuperuser

Celery command
- celery -A psims_web_project  worker -l info --pool=gevent


Redis command
- redis-server


