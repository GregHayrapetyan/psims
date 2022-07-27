import datetime
import xarray
from datetime import datetime, timedelta, date
import os



def planting_hint(crop, lat, lon):
    dir  = os.getcwd()
    nc_dir = dir + '/psims/planting_data'
    
    nc_files = {
        "barley": f"/web/psims_web/psims/planting_data/Barley.crop.calendar.fill.nc",
        "canola": f"/web/psims_web/psims/planting_data/Rapeseed.Winter.crop.calendar.fill.nc",
        "corn": f"/web/psims_web/psims/planting_data/Maize.crop.calendar.fill.nc",
        "cotton": f"/web/psims_web/psims/planting_data/Cotton.crop.calendar.fill.nc",
        "rice": f"/web/psims_web/psims/planting_data/Rice.crop.calendar.fill.nc",
        "sorghum": f"/web/psims_web/psims/planting_data/Sorghum.crop.calendar.fill.nc",
        "soybean": f"/web/psims_web/psims/planting_data/Soybeans.crop.calendar.fill.nc",
        "spring_wheat": f"/web/psims_web/psims/planting_data/Wheat.crop.calendar.fill.nc",
        "winter_wheat": f"/web/psims_web/psims/planting_data/Wheat.Winter.crop.calendar.fill.nc",
    }

    try:
        crop = crop.lower().replace(" ", "_")
        nc = xarray.open_dataset(nc_files[crop])
        doy = nc.sel(latitude=lat, longitude=lon, method="nearest").plant
        pdate = datetime(datetime.now().year, 1, 1) + timedelta(int(doy) - 1)
        p = pdate.date()
        pdate_day = p.timetuple().tm_yday
        return pdate_day
     
    except Exception as e:
        print(e)
        return e
