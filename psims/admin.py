from django.contrib import admin
from datetime import datetime
from .models import *



class CropId(admin.ModelAdmin):
    readonly_fields = ('id',)
    
admin.site.register(Weather)
admin.site.register(Location)
admin.site.register(Crop, CropId)
admin.site.register(Product)
admin.site.register(IrrigationMethod)
admin.site.register(TillageImplement)
admin.site.register(FertilizerMethod)
admin.site.register(FertilizerType)
admin.site.register(FertilizationParameters)
admin.site.register(PlantingParameters)
admin.site.register(Profile)
admin.site.register(Card)
admin.site.register(CardTitle)



@admin.register(PsimsOutput)
class EcoProductAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'owner', 'average_yield',  'get_planting_date']
    list_filter = ('created_at','owner')
    search_fields = ['owner__username__icontains']
    
    def get_planting_date(self, obj):
        if obj.planting_day == None:
            return "Hasn't PD"
        else:
            day_num = str(obj.planting_day.planting_date)
            day_num.rjust(3 + len(day_num), '0')
            now = datetime.now()
            year = str(now.year)          
            res = datetime.strptime(year + "-" + day_num, "%Y-%j").strftime("%m-%d-%Y")
            return res 
        
    get_planting_date.admin_order_field  = 'planting_day'  #Allows column order sorting
    get_planting_date.short_description = 'Planting date'  #Renames column head