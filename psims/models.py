from statistics import mode
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from django.db.models.expressions import Value
from django.db.models.fields import CharField
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime


class PsimsUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='psims_worker')
    is_seen = models.BooleanField('Is user seen last message?', default=False)
    completed_worker_id = models.IntegerField('Complated worker id', default=0)
    
    def __str__(self):
        return self.user.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.CharField(max_length=30, default='')
    phone_number = models.CharField(max_length=60, blank=True,  default='')
    title = models.CharField(max_length=30, blank=True, default='')
    crops_regions = models.CharField(max_length=30, blank=True, default='')
    is_paid = models.BooleanField(default=False)
    def __str__(self):
        return self.user.username


class Card(models.Model):
    name = models.CharField(max_length=150)
    number = models.FloatField()
    value = models.CharField(max_length=30)
    description = models.CharField(max_length=100, blank=True, null=True)
    updated_time = models.DateTimeField('date_published', auto_now=True)

    def __str__(self):
        return self.name

class CardTitle(models.Model):
    title = models.CharField(max_length=300)
    class Meta:
        verbose_name_plural = "Card Title"
    def __str__(self):
        return 'Card Title'

class PsimsYesNoField(models.BooleanField):
    def __init__(self, name=None, name_long=None, units=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.name_long = name_long
        self.units = units
        self.verbose_name = f"{self.name_long}"

    class Meta:
        abstract = True


class PsimsDecimalField(models.DecimalField):
    def __init__(self, name=None, name_long=None, units=None, max_digits=6, decimal_places=2, *args,
                 **kwargs):
        kwargs['max_digits'] = max_digits
        kwargs['decimal_places'] = decimal_places
        super().__init__(*args, **kwargs)
        self.name = name
        self.name_long = name_long
        self.units = units
        self.verbose_name = f"{self.name_long} ({self.units})"

    class Meta:
        abstract = True


class PsimsFloatField(models.FloatField):
    def __init__(self, name=None, name_long=None, units=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.name_long = name_long
        self.units = units
        if self.units:
            self.verbose_name = f"{self.name_long} ({self.units})"
        else:
            self.verbose_name = self.name_long

    class Meta:
        abstract = True


class PsimsIntegerField(models.IntegerField):
    def __init__(self, name=None, name_long=None, units=None, default=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.name_long = name_long
        self.units = units
        self.verbose_name = f"{self.name_long}"
        self.default = default

        if self.units:
            self.verbose_name += f' ({self.units})'

    class Meta:
        abstract = True


class PsimsCharField(models.CharField):
    def __init__(self, name=None, name_long=None, units=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.name_long = name_long
        self.units = units
        if self.units:
            self.verbose_name = f"{self.name_long} ({self.units})"
        else:
            self.verbose_name = self.name_long

    class Meta:
        abstract = True


class PlantingParameters(models.Model):
    planting_date = PsimsIntegerField(name="planting_date",
                                      name_long="Select Planting Date",
                                      validators=[
                                         MinValueValidator(1),
                                         MaxValueValidator(366),
                                      ])
    plant_population  = PsimsIntegerField(name="plplp",
                                       name_long="Target planting density",
                                       units="plants/m2",
                                       default=None,
                                       blank=True,
                                       null=True)
    planting_depth = PsimsIntegerField(name="pldp",
                                       name_long="Planting Depth",
                                       units="mm",
                                       default=25)
    row_spacing = PsimsIntegerField(name="plrs",
                                    name_long="Row Spacing",
                                    units="mm",
                                    default=75)
    planting_population_at_planting = PsimsIntegerField(name="plpop",
                                                        name_long="Plant population at planting",
                                                        units="plants/m2",
                                                        default=None)
    planting_population_at_emergence = PsimsIntegerField(name="plpoe",
                                                         name_long="Planting population at "
                                                                   "emergence",
                                                         units="plants/m2",
                                                         default=None)
    use_irrigation = PsimsYesNoField(name="irrig",
                                     name_long="Use irrigation?",
                                     units="true/false",
                                     default=False)
    
    irrigation_method = PsimsCharField(name="iame",
                                       name_long="Irrigation method",
                                       units="make selection",
                                       default="IR001",
                                       max_length=20)
    

class FertilizationParameters(models.Model):
    fertilizer_doy = PsimsIntegerField(name="fertilizer_date",
                                       name_long="Fertilizer Application Date",
                                       default=1,
                                       validators=[
                                         MinValueValidator(0),
                                         MaxValueValidator(366),
                                       ])
    fertilizer_amount = PsimsIntegerField(name="feamn",
                                          name_long="Nitrogen in applied fertilizer",
                                          units="kg N / ha",
                                          default=100)
    fertilizer_depth = PsimsIntegerField(name="fedep",
                                         name_long="Fertilizer application depth",
                                         units="cm",
                                         default=15)



class TillageParameters(models.Model):
    use_tillage = PsimsYesNoField(name="till", name_long="Use tillage?", units="yes/no",
                                  default=False)
    tillage_implement = PsimsCharField(name="tiimp",
                                       name_long="Tillage implement",
                                       units="make selection",
                                       default="unknown",
                                       max_length=20)
    tillage_depth = PsimsIntegerField(name="tidep",
                                      name_long="Tillage operations depth",
                                      units="cm", default=5)


class Crop(models.Model):
    name = models.CharField(max_length=20, default="unnamed_crop")
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Weather(models.Model):
    name = models.CharField(max_length=20, default="unnamed weather")
    description = models.CharField(max_length=2000, default="generic description")

    def __str__(self):
        return self.name


class IrrigationMethod(models.Model):
    name = models.CharField(max_length=10, default="unnamed_method")
    name_long = models.CharField(max_length=50, default="unnamed_code")
    units = models.CharField(max_length=20, default="unnamed_units")

    def __str__(self):
        return self.name


class TillageImplement(models.Model):
    name = models.CharField(max_length=20, default="unnamed")
    name_long = models.CharField(max_length=70, default="unnamed")

    def __str__(self):
        return self.name_long


class CornParameters(models.Model):

    # cultivar parameters
    p1 = PsimsIntegerField(name="p1",
                           name_long="Degree days (base 8C) from emergence to end of juvenile phase",
                           default=300,
                           units="days")
    p2 = PsimsFloatField(name="p2",
                         name_long="Photoperiod sensitivity coefficient",
                         units="0/1.0",
                         default=0.75)
    p5 = PsimsIntegerField(name="p5",
                           name_long="Degree days (base 8C) from silking to physiological maturity",
                           units="days",
                           default=800)
    g2 = PsimsIntegerField(name="g2",
                           name_long="Maximum possible number of kernels per plant",
                           units="mg/(kernel d)",
                           default=850)
    g3 = PsimsFloatField(name="g3",
                         name_long="Kernel filling rate during the linear grain filling stage and under optimum "
                                   "conditions",
                         units="mg/day",
                         default=9.5)
    phint = PsimsFloatField(name="phint",
                            name_long="Phylochron interval; the interval in thermal time between successive leaf tip appearances",
                            units="degree days",
                            default=8)

    # ecotype parameters
    tbase = PsimsIntegerField(name="tbase",
                              name_long="Base temperature below which no development occurs",
                              units="C",
                              default=8)
    topt = PsimsIntegerField(name="topt",
                             name_long="Temperature at which maximum development rate occurs "
                                       "during vegetative stages",
                             units="C",
                             default=34)
    ropt = PsimsIntegerField(name="ropt",
                             name_long="Temperature at which maximum development rate occurs for "
                                       "reproductive stages",
                             units="C",
                             default=34)
    p2O = PsimsFloatField(name="p20",
                          name_long="Daylength below which daylength does not affect development "
                                    "rate",
                          units="hours",
                          default=12.5)
    djti = PsimsIntegerField(name="djti",
                             name_long="Minimum days from end of juvenile stage to tassel "
                                       "initiation of the cultivar",
                             units="days",
                             default=4.0)
    gdde = PsimsIntegerField(name="gdde",
                             name_long="Growing degree days per cm seed depth required for "
                                       "emergence",
                             units="GDD/cm",
                             default=6.0)
    dsgft = PsimsIntegerField(name="dsgft",
                              name_long="GDD from silking to effective grain filling period",
                              units="C",
                              default=170.0)
    rue = PsimsFloatField(name="rue",
                          name_long="Radiation use efficiency",
                          units="g plant dry matter/MJ PAR",
                          default=4.3)
    kcan = PsimsFloatField(name="kcan",
                           name_long="Canopy light extinction coefficient for daily PAR",
                           units="coefficient",
                           default=0.85)


class SoybeanParameters(models.Model):

    # cultivar parameters
    csdl = PsimsFloatField(name="csdl",
                           name_long="Critical short day length below which reproductive "
                                     "development progresses with no daylength effect ("
                                     "for short day plants)",
                           units="hours",
                           default=14.60)
    ppsen = PsimsFloatField(name="ppsen",
                            name_long="Slope of the relative response of development to photoperiod with time",
                            units="1/hour",
                            default=0.129)
    emfl = PsimsFloatField(name="em-fl",
                             name_long="Time between plant emergence and flower appearance (R1)",
                             units="days",
                             default=23)
    flsh = PsimsFloatField(name="fl-sh",
                             name_long="Time between first flower and first pod (R3)",
                             units="days",
                             default=7.5)
    flsd = PsimsFloatField(name="fl-sd",
                             name_long="Time between first flower and first seed (R5)",
                             units="days",
                             default=18)
    sdpm = PsimsFloatField(name="sd-pm",
                             name_long="Time between first seed (R5) and physiological maturity ("
                                       "R7)",
                             units="days",
                             default=33)
    fllf = PsimsFloatField(name="fl-lf",
                             name_long="Time between first flower (R1) and end of leaf expansion",
                             units="days",
                             default=39)
    lfmax = PsimsFloatField(name="lfmax",
                            name_long="Maximum leaf photosynthesis rate at 30 C, 350 vpm CO2, and high light",
                            units="mg CO2/m2-s",
                            default=1.03)
    slavr = PsimsFloatField(name="slavr",
                            name_long="Specific leaf area of cultivar under standard growth conditions",
                            units="cm2/g",
                            default=375)
    sizlf = PsimsFloatField(name="sizlf",
                            name_long="Maximum size of full leaf",
                            units="cm2",
                            default=180)
    xfrt = PsimsFloatField(name="xfrt",
                           name_long="Maximum fraction of daily growth that is partitioned to seed + shell",
                           units="fraction",
                           default=1)
    wtpsd = PsimsFloatField(name="wtpsd",
                            name_long="Maximum weight per seed",
                            units="weight",
                            default=0.19)
    sfdur = PsimsFloatField(name="sfdur",
                            name_long="Seed filling duration for pod cohort at standard growth conditions",
                            units="photothermal days",
                            default=23)
    sdpdv = PsimsFloatField(name="sdpdv",
                            name_long="Average seed per pod under standard growing conditions",
                            units="seed per pod",
                            default=2.2)
    podur = PsimsFloatField(name="podur",
                            name_long="Time required for cultivar to reach final pod load under optimal conditions",
                            units="photothermal days",
                            default=10)
    thrsh = PsimsFloatField(name="thrsh",
                            name_long="Threshing percentage. The maximum ratio of (seed/(seed+shell)) at maturity. "
                                      "Causes seeds to stop growing as their dry weight increases until shells are "
                                      "filled in a cohort",
                            units="percentage",
                            default=77)
    sdpro = PsimsFloatField(name="sdpro",
                            name_long="Fraction protein in seeds",
                            units="percentage",
                            default="0.405")
    sdlip = PsimsFloatField(name="sdlip",
                            name_long="Fraction oil in seeds",
                            units="percentage",
                            default=0.205)

    # ecotype parameters
    mg = PsimsIntegerField(name="mg",
                           name_long="Maturity group number",
                           units="integer",
                           default=1)
    tm = PsimsIntegerField(name="tm",
                           name_long="Indicator of temperature adaptation",
                           units="integer",
                           default=1)
    thvar = PsimsFloatField(name="thvar",
                            name_long="Minimum rate of reproductive development under long days and optimal "
                                      "temperature",
                            units="rate",
                            default=0)
    plem = PsimsFloatField(name="pl-em",
                           name_long="Time between planting and emergence (V0)",
                           units="thermal days",
                           default=3.60)
    emv1 = PsimsFloatField(name="em-v1",
                           name_long="Time required from emergence to first true leaf (V1)",
                           units="thermal days",
                           default=6.0)
    v1ju = PsimsFloatField(name="v1-ju",
                           name_long="Time required from first true leaf to end of juvenile phase",
                           units="thermal days",
                           default=0.0)
    jur0 = PsimsFloatField(name="ju-r0",
                           name_long="Time required for floral induction, equal to the minimum "
                                     "number of days for floral induction, under optimal "
                                     "temperature and daylengths",
                           units="photothermal days",
                           default=5.0)
    pm06 = PsimsFloatField(name="pm06",
                           name_long="Proportion of time between first flower and first pod for first peg",
                           units="peanut only",
                           default=0)
    pm09 = PsimsFloatField(name="pm09",
                           name_long="Proportion of time between first seed and physiological maturity that the last "
                                     "seed can be formed",
                           units="proportion",
                           default=0.35)
    lngsh = PsimsFloatField(name="lngsh",
                            name_long="Time required for growth of individual shells",
                            units="photothermal days",
                            default=10)
    r7r8 = PsimsFloatField(name="r7-r8",
                           name_long="Time between physiological (R7) and harvest maturity (R8)",
                           units="days",
                           default=12)
    flvs = PsimsFloatField(name="fl-vs",
                           name_long="Time from first flower to last leaf on main stem",
                           units="photothermal days",
                           default=26.0)
    trifl = PsimsFloatField(name="trifl",
                            name_long="Rate of appearance of leaves on the mainstem",
                            units="leaves per thermal day",
                            default=0.32)
    rwdth = PsimsFloatField(name="rwdth",
                            name_long="Relative width of this ecotype in comparison to the standard width per node "
                                      "(YVSWH) defined in the species file",
                            units="*.SPE",
                            default=1)
    rhght = PsimsFloatField(name="rhght",
                            name_long="Relative height of this ecotype in comparison to the standard height per node "
                                      "(YVSHT) defined in the species file",
                            units="*.SPE",
                            default=1)
    r1ppo = PsimsFloatField(name="r1ppo",
                            name_long="Increase in daylength sensitivity after R1",
                            units="h",
                            default=0.234)
    optbi = PsimsFloatField(name="optbi",
                            name_long="Minimum daily temperature above which there is no effect "
                                      "on slowing normal development toward "
                                      "flowering",
                            units="C",
                            default=18.0)
    slobi = PsimsFloatField(name="slobi",
                            name_long="Slope of relationship reducing progress toward flowering if TMIN for the day is "
                                      "less than OPTBI",
                            units="slope",
                            default=0.028)


class HempParameters(models.Model):

    # cultivar parameters
    csdl = PsimsFloatField(name="csdl",
                           name_long="Critical short day length below which reproductive "
                                     "development progresses with no daylength effect ("
                                     "for short day plants)",
                           units="hours",
                           default=13.09)
    ppsen = PsimsFloatField(name="ppsen",
                            name_long="Slope of the relative response of development to photoperiod with time",
                            units="1/hour",
                            default=0.294)
    emfl = PsimsFloatField(name="em-fl",
                             name_long="Time between plant emergence and flower appearance (R1)",
                             units="days",
                             default=19.4)
    flsh = PsimsFloatField(name="fl-sh",
                             name_long="Time between first flower and first pod (R3)",
                             units="days",
                             default=7)
    flsd = PsimsFloatField(name="fl-sd",
                             name_long="Time between first flower and first seed (R5)",
                             units="days",
                             default=15)
    sdpm = PsimsFloatField(name="sd-pm",
                             name_long="Time between first seed (R5) and physiological maturity ("
                                       "R7)",
                             units="days",
                             default=34)
    fllf = PsimsFloatField(name="fl-lf",
                             name_long="Time between first flower (R1) and end of leaf expansion",
                             units="days",
                             default=26)
    lfmax = PsimsFloatField(name="lfmax",
                            name_long="Maximum leaf photosynthesis rate at 30 C, 350 vpm CO2, and high light",
                            units="mg CO2/m2-s",
                            default=1.03)
    slavr = PsimsFloatField(name="slavr",
                            name_long="Specific leaf area of cultivar under standard growth conditions",
                            units="cm2/g",
                            default=375)
    sizlf = PsimsFloatField(name="sizlf",
                            name_long="Maximum size of full leaf",
                            units="cm2",
                            default=180)
    xfrt = PsimsFloatField(name="xfrt",
                           name_long="Maximum fraction of daily growth that is partitioned to seed + shell",
                           units="fraction",
                           default=1)
    wtpsd = PsimsFloatField(name="wtpsd",
                            name_long="Maximum weight per seed",
                            units="weight",
                            default=0.19)
    sfdur = PsimsFloatField(name="sfdur",
                            name_long="Seed filling duration for pod cohort at standard growth conditions",
                            units="photothermal days",
                            default=23)
    sdpdv = PsimsFloatField(name="sdpdv",
                            name_long="Average seed per pod under standard growing conditions",
                            units="seed per pod",
                            default=2.2)
    podur = PsimsFloatField(name="podur",
                            name_long="Time required for cultivar to reach final pod load under optimal conditions",
                            units="photothermal days",
                            default=10)
    thrsh = PsimsFloatField(name="thrsh",
                            name_long="Threshing percentage. The maximum ratio of (seed/(seed+shell)) at maturity. "
                                      "Causes seeds to stop growing as their dry weight increases until shells are "
                                      "filled in a cohort",
                            units="percentage",
                            default=77)
    sdpro = PsimsFloatField(name="sdpro",
                            name_long="Fraction protein in seeds",
                            units="percentage",
                            default="0.405")
    sdlip = PsimsFloatField(name="sdlip",
                            name_long="Fraction oil in seeds",
                            units="percentage",
                            default=0.205)



class DefaultParameters(models.Model):
    p1 = PsimsIntegerField(name="p1",
                           name_long="TBD-Degree days (base 8C) from emergence to end of juvenile phase",
                           default=82,
                           units="days")
    p2 = PsimsFloatField(name="p2",
                         name_long="TBD-Photoperiod sensitivity coefficient",
                         units="0/1.0",
                         default=0.75)
    p5 = PsimsIntegerField(name="p5",
                           name_long="TBD-Degree days (base 8C) from silking to physiological maturity",
                           units="days",
                           default=525)
    tbase = PsimsIntegerField(name="TBASE",
                              name_long="TBD-Base temperature below which no development occurs",
                              units="C",
                              default=8)
    topt = PsimsIntegerField(name="TOPT",
                             name_long="TBD-Temperature at which maximum development rate occurs "
                                       "during vegetative stages",
                             units="C",
                             default=34)
    ropt = PsimsIntegerField(name="ROPT",
                             name_long="TBD-Temperature at which maximum development rate occurs for "
                                       "reproductive stages",
                             units="C",
                             default=34)
    p2O = PsimsFloatField(name="P2O",
                          name_long="TBD-Daylength below which daylength does not affect development "
                                    "rate",
                          units="hours",
                          default=12.5)
    djti = PsimsIntegerField(name="DJTI",
                             name_long="TBD-Minimum days from end of juvenile stage to tassel "
                                       "initiation of the cultivar",
                             units="days",
                             default=4.0)
    gdde = PsimsIntegerField(name="GDDE",
                             name_long="TBD-Growing degree days per cm seed depth required for "
                                       "emergence",
                             units="GDD/cm",
                             default=6.0)
    dsgft = PsimsIntegerField(name="DSGFT",
                              name_long="TBD-GDD from silking to effective grain filling period",
                              units="C",
                              default=170.0)
    rue = PsimsFloatField(name="RUE",
                          name_long="TBD-Radiation use efficiency",
                          units="g plant dry matter/MJ PAR",
                          default=4.3)
    kcan = PsimsFloatField(name="KCAN",
                           name_long="TBD-Canopy light extinction coefficient for daily PAR",
                           units="coefficient",
                           default=0.85)
    tsen = PsimsIntegerField(name="TSEN",
                             name_long="TBD-Critical temperature below which leaf damage occurs ("
                                       "default 6°C), is not photoperiod sensitive",
                             units="days",
                             default=6.0)
    cday = PsimsIntegerField(name="CDAY",
                             name_long="TBD-Number of cold days parameter",
                             units="days",
                             default=15.0)


class FertilizerMethod(models.Model):
    name = models.CharField(max_length=10)
    name_long = models.CharField(max_length=70)

    def __str__(self):
        return self.name_long


class FertilizerType(models.Model):
    name = models.CharField(max_length=10)
    name_long = models.CharField(max_length=70)

    def __str__(self):
        return self.name_long


class Location(models.Model):
    latitude = models.FloatField(default=39.43530142067006, validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.FloatField(default=-92.34310605480388, validators=[MinValueValidator(-180),
                                                                          MaxValueValidator(180)])
    polygon_data = models.TextField(null=True, blank=True)
    multy_markers =  models.TextField(null=True, blank=True)  
    location_names = models.TextField(null=True, blank=True)                                                            
    name = models.CharField(default="Location name", max_length=128)

    def __str__(self):
        return self.name


class Pricing(models.Model):
    get_pricing = PsimsYesNoField(default=False, name="pricing", name_long="Get indicative "
                                                                           "pricing?")
    strike = PsimsIntegerField(default=90, units="% of normal", name="strike",
                               name_long="Strike", validators=[MinValueValidator(0),
                                                               MaxValueValidator(100)])
    full_payout = PsimsIntegerField(default=70, units="% of normal", name="full_payout",
                                    name_long="Full payout", validators=[MinValueValidator(0),
                                                                         MaxValueValidator(100)])
    desired_coverage = PsimsIntegerField(default=1000, units="$", name="desired_coverage",
                                         name_long="Amount of desired coverage",
                                         validators=[MinValueValidator(1)])


class RiceParameters(models.Model):
    # cultivar params
    p1 = PsimsFloatField(name="p1",
                         name_long="Degree days (base 8C) from emergence to end of juvenile phase",
                         default=500,
                         units="celsius GDD")
    p2r = PsimsFloatField(name="p2r",
                          name_long="Extent to which phasic development leading to panicle initiation is delayed",
                          default=30,
                          units="celsius GDD")
    p5 = PsimsFloatField(name="p5",
                         name_long="Time period in from beginning of grain filling to physiological maturity",
                         units="celcius GDD",
                         default=500)
    p2O = PsimsFloatField(name="p2O",
                          name_long="Critical photoperiod or the longest day length (in hours) at which the "
                                    "development occurs at a maximum rate",
                          default=12,
                          units="hours")
    g1 = PsimsFloatField(name="g1",
                         name_long="Potential spikelet number coefficient",
                         units="spikelets per g of main culm dry weight ",
                         default=55)
    g2 = PsimsFloatField(name="g2",
                         name_long="Single grain weight under ideal growing conditions",
                         units="g",
                         default=0.025)
    g3 = PsimsFloatField(name="g3",
                         name_long="Tillering coefficient",
                         units="scalar value",
                         default=1)
    g4 = PsimsFloatField(name="g4",
                         name_long="Temperature tolerance coefficient",
                         units="constant",
                         default=1)
    phint = PsimsFloatField(name="phint",
                            name_long="phint",
                            units="value",
                            default=83)
 


class SugarcaneParameters(models.Model):

    # cultivar parameters
    maxparce = PsimsFloatField(name="maxparce",
                               name_long="Maximum (no stress) radiation conversion efficiency expressed as "
                                           "assimilate  produced before respiration, per unit PAR.",
                               units="g/MJ",
                               default=9.9)
    apfmx = PsimsFloatField(name="apfmx",
                            name_long="Maximum fraction of dry mass increments that can be allocated to aerial dry "
                                      "mass",
                            units="t/t",
                            default=0.88)
    stkpfmax = PsimsFloatField(name="stkpfmax",
                               name_long="Fraction of daily aerial dry mass increments partitioned to stalk at high "
                                         "temperatures in a mature crop",
                               units="t/t",
                               default=0.65)
    suca = PsimsFloatField(name="suca",
                           name_long="Maximum sucrose contents in the base of stalk",
                           units="t/t",
                           default=0.58)
    tbft = PsimsFloatField(name="tbft",
                           name_long="Temperature at which partitioning of unstressed stalk mass increments to sucrose is 50% of the maximum value",
                           units="c",
                           default=25)
    tthalfo = PsimsFloatField(name="tthalfo",
                              name_long="Thermal time to half canopy",
                              units="oCd",
                              default=250)
    tbase = PsimsFloatField(name="tbase",
                            name_long="Base temperature for canopy development",
                            units="oCd",
                            default=16)
    lfmax = PsimsFloatField(name="lfmax",
                            name_long="Maximum number of green leaves a healthy, adequately-watered plant will have "
                                       "after it is old enough to lose some leaves",
                            units="count",
                            default=12)
    mxlfarea = PsimsFloatField(name="mxlfarea",
                               name_long="Max leaf area assigned to all leaves above leaf number MXLFARNO",
                               units="cm2",
                               default=360)
    mxlfarno = PsimsFloatField(name="mxlfarno",
                               name_long="Leaf number above which leaf area is limited to MXLFAREA",
                               units="count",
                               default=14)
    pi1 = PsimsFloatField(name="pi1",
                          name_long="Phyllocron interval 1 for leaf numbers below Pswitch",
                          units="oCd",
                          default=69)
    pi2 = PsimsFloatField(name="pi2",
                          name_long="Phyllocron interval 2 for leaf numbers above Pswitch",
                          units="oCd",
                          default=169)
    pswitch = PsimsFloatField(name="pswitch",
                              name_long="Leaf number at which the phyllocron changes",
                              units="count",
                              default=18)
    ttplntem = PsimsFloatField(name="ttplntem",
                               name_long="Thermal time to emergence for a plant crop",
                               units="c GDU",
                               default=428)
    ttratnem = PsimsFloatField(name="ttratnem",
                               name_long="Thermal time to emergence for a ratoon crop",
                               units="c GDU",
                               default=203)
    chupibase = PsimsFloatField(name="chupibase",
                                name_long="Thermal time from emergence to start of stalk growth",
                                units="c GDU",
                                default=1050)
    tt_popgrowth = PsimsFloatField(name="tt_popgrowth",
                                   name_long="Thermal time to peak tiller population",
                                   units="c GDU",
                                   default=600)
    max_pop = PsimsFloatField(name="max_pop",
                              name_long="Maximum tiller population",
                              units="stalks/m2",
                              default=30)
    poptt16 = PsimsFloatField(name="poptt16",
                              name_long="Stalk population at/after 1600 degree days",
                              units="stalks/m2",
                              default=13.3)
    lg_ambase = PsimsFloatField(name="lg_ambase",
                                name_long="Aerial mass (fresh mass of stalks, leaves, and water attached to them) "
                                          "at which lodging starts",
                                units="t/ha",
                                default=220)

    # ecotype parameters
    DELTTMAX = PsimsDecimalField(name="DELTTMAX",
                                 name_long="Max. change in sucrose content per unit change in stalk mass in the "
                                           "unripenened section of the stalk (/t)",
                                 units="t/t",
                                 default=0.07)
    CS_CNREDUC = PsimsDecimalField(name="CS_CNREDUC",
                                   name_long="Canopy reduction due to water stress",
                                   units="fraction",
                                   default=0.3)
    DPERdT = PsimsDecimalField(name="DPERdT",
                               name_long="Change in plant extension rate (mm/h) per unit change in temperature",
                               units="count",
                               default=0.17)
    EXTCFN = PsimsDecimalField(name="EXTCFN",
                               name_long="Maximum canopy light extinction coefficient",
                               units="constant",
                               default=0.84)
    EXTCFST = PsimsDecimalField(name="EXTCFST",
                                name_long="Minimum canopy light extinction coefficient",
                                units="constant",
                                default=0.58)
    LFNMXEXT = PsimsIntegerField(name="LFNMXEXT",
                                 name_long="Leaf number (including dead leaves still attached) at which maximum light "
                                           "extinction occurs",
                                 units="count",
                                 default=20)
    TTBASEEM = PsimsIntegerField(name="TTBASEEM",
                                 name_long="Base temperature for emergence",
                                 units="c",
                                 default=10)
    TTBASELFEX = PsimsIntegerField(name="TTBASELFEX",
                                   name_long="Base temperature for leaf phenology",
                                   units="c",
                                   default=10)
    TTBASEPOP = PsimsIntegerField(name="TTBASEPOP",
                                  name_long="Base temperature for stalk phenology",
                                  units="c",
                                  default=16)
    TBASEPER = PsimsDecimalField(name="TBASEPER",
                                 name_long="Base temperature for plant extension",
                                 units="c",
                                 default=10.57)
    LG_AMRANGE = PsimsIntegerField(name="LG_AMRANGE",
                                   name_long="Range in aerial mass from the start to the end of lodging",
                                   units="t/ha",
                                   default=30)
    LG_GP_REDUC = PsimsDecimalField(name="LG_GP_REDUC",
                                    name_long="Reduction in gross photosynthesis due to full lodging, as a fraction",
                                    units="fraction",
                                    default=0.28)
    LG_FI_REDUC = PsimsDecimalField(name="LG_FI_REDUC",
                                    name_long="Reduction in fractional interception by the canopy due to full lodging",
                                    units="fraction",
                                    default=0.1)


# TODO: revisit
# class Index(models.Model):
#     title = "Name your Index"
#     name = models.CharField(default="New Index", max_length=128)


class PsimsOutput(models.Model):
    proccess_id = models.CharField(default=0, null=True, max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    json = models.JSONField()
    owner = models.ForeignKey(User, verbose_name='User', on_delete=models.CASCADE, default=1)
    average_yield = models.FloatField(max_length=20, null=True)
    last_yield = models.FloatField(null=True)
    last_year = models.IntegerField(null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE,  null=True)
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, null=True)
    # weather = models.ForeignKey(Weather, on_delete=models.CASCADE, null=True)
    # irrigation_parameters = models.ForeignKey(IrrigationParameters, on_delete=models.CASCADE, null=True)
    planting_day = models.ForeignKey(PlantingParameters, on_delete=models.CASCADE, null=True)
    fertilizer_day = models.ForeignKey(FertilizationParameters, on_delete=models.CASCADE, null=True)
    long_names = models.JSONField(null=True)
    last_step_json = models.JSONField(null=True)
    is_open = models.BooleanField(default=False)
    weighted_index = models.IntegerField(null=True, blank=True)
    is_weighted_index = models.BooleanField(default=False)
    is_era = models.BooleanField(default=False)
    is_live =models.BooleanField(default=False)
    is_parent = models.BooleanField(default=False)
    parent = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    def __str__(self):
        simple_time = f"{self.created_at.year:04}-{self.created_at.month:02}-{self.created_at.day:02} " \
                      f"{self.created_at.hour:02}:{self.created_at.minute:02} "
        return f"{simple_time}"

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)  # cents
    file = models.FileField(upload_to="product_files/", blank=True, null=True)
    url = models.URLField(default='127.0.0.1:8000')
    def __str__(self):
        return self.name
    
    def get_display_price(self):
        return "{0:.2f}".format(self.price / 100)



class SpringWheatParameters(models.Model):

    # cultivar parameters
    p1v = PsimsFloatField(name="p1v",
                          name_long="Optimum vernalizing temperature, required for vernalization",
                          units="days",
                          default=5)
    p1d = PsimsFloatField(name="p1d",
                          name_long="Photoperiod response",
                          units="% reduction in rate/10 h drop in pp",
                          default=100)
    p5 = PsimsFloatField(name="p5",
                         name_long="Grain filling (excluding lag) phase duration",
                         units="GDD celsius",
                         default=500)
    g1 = PsimsFloatField(name="g1",
                         name_long="Kernel number per unit canopy weight at anthesis",
                         units="Kernels per gram",
                         default=25)
    g2 = PsimsFloatField(name="g2",
                         name_long="Standard kernel size under optimum conditions",
                         units="mg",
                         default=30)
    g3 = PsimsFloatField(name="g3",
                         name_long="Standard, non-stressed mature tiller weight",
                         units="g",
                         default=2.5)
    phint = PsimsFloatField(name="phint",
                            name_long="Interval between successive leaf tip appearances",
                            units="GDD celsius",
                            default=86)

    # ecotype parameters
    gnmn = PsimsFloatField(name="gn%mn",
                           name_long="Minimum grain N",
                           units="% by weight",
                           default=1.5)
    # gns = PsimsFloatField(name="gn%s",
    #                       name_long="Standard grain N",
    #                       units="% by weight",
    #                       default=3)
    HTSTD = PsimsIntegerField(name="HTSTD",
                              name_long="Standard canopy height",
                              units="cm",
                              default=100)
    LA1S = PsimsIntegerField(name="LA1S",
                             name_long="Area of standard first leaf",
                             units="cm2",
                             default=5)
    LAFR = PsimsDecimalField(name="LAFR",
                             name_long="Increase in potential area of leaves, reproductive phase",
                             units="fraction per leaf",
                             default=0.5)
    LAFV = PsimsDecimalField(name="LAFV",
                             name_long="Increase in potential area of leaves,vegetative phase",
                             units="fraction per leaf",
                             default=0.1)
    P1 = PsimsIntegerField(name="P1",
                           name_long="Duration of phase end juvenile to terminal spikelet",
                           units="GDD celsius",
                           default=200)
    P2 = PsimsIntegerField(name="P2",
                           name_long="Duration of phase terminal spikelet to end leaf growth",
                           units="GDD celsius",
                           default=200)
    P2FR1 = PsimsDecimalField(name="P2FR1",
                              name_long="Duration of phase terminal spikelet to jointing",
                              units="fr P2",
                              default=0.25)
    P3 = PsimsIntegerField(name="P3",
                           name_long="Duration of phase end leaf growth to end spike growth",
                           units="GDD celsius",
                           default=200)
    P4 = PsimsIntegerField(name="P4",
                           name_long="Duration of phase end spike growth to end grain fill lag",
                           units="GDD celsius",
                           default=200)
    P4FR1 = PsimsDecimalField(name="P4FR1",
                              name_long="Duration of phase end spike growth to anthesis",
                              units="fr P4",
                              default=0.25)
    P4FR2 = PsimsDecimalField(name="P4FR2",
                              name_long="Duration of phase anthesis start to anthesis end",
                              units="fr P4",
                              default=0.1)
    RDGS = PsimsIntegerField(name="RDGE",
                             name_long="Root depth growth rate,early phase",
                             units="cm per standard depth",
                             default=3)
    RSS = PsimsDecimalField(name="RS%S",
                            name_long="Reserves part of assimilates going to stem",
                            units="%",
                            default=30)
    SLAS = PsimsIntegerField(name="SLAS",
                             name_long="Specific leaf area,standard first leaf",
                             units="cm2/g",
                             default=400)
    TKFH = PsimsIntegerField(name="TKFH",
                             name_long="Temperature at which killed when fully hardened",
                             units="celsius",
                             default=-10)


class WinterWheatParameters(models.Model):
    # cultivar parameters
    p1v = PsimsFloatField(name="p1v",
                          name_long="Optimum vernalizing temperature, required for vernalization",
                          units="days",
                          default=5)
    p1d = PsimsFloatField(name="p1d",
                          name_long="Photoperiod response",
                          units="% reduction in rate/10 h drop in pp",
                          default=100)
    p5 = PsimsFloatField(name="p5",
                         name_long="Grain filling (excluding lag) phase duration",
                         units="GDD celsius",
                         default=500)
    g1 = PsimsFloatField(name="g1",
                         name_long="Kernel number per unit canopy weight at anthesis",
                         units="Kernels per gram",
                         default=25)
    g2 = PsimsFloatField(name="g2",
                         name_long="Standard kernel size under optimum conditions",
                         units="mg",
                         default=30)
    g3 = PsimsFloatField(name="g3",
                         name_long="Standard, non-stressed mature tiller weight",
                         units="g",
                         default=2.5)
    phint = PsimsFloatField(name="phint",
                            name_long="Interval between successive leaf tip appearances",
                            units="GDD celsius",
                            default=86)



class CottonParameters(models.Model):

    # cultivar parameters
    csdl = PsimsFloatField(name="csdl",
                           name_long="Critical Short Day Length below which reproductive development progresses "
                                     "with no daylength effect for shortday plants",
                           units="hours",
                           default=23)
    ppsen = PsimsFloatField(name="ppsen",
                            name_long="Slope of the relative response of development to photoperiod with time (positive for shortday plants)",
                            units="1/hour",
                            default=0.01)
    emfl = PsimsFloatField(name="em-fl",
                           name_long="Time between plant emergence and flower appearance",
                           units="photothermal days",
                           default=50)
    flsh = PsimsFloatField(name="fl-sh",
                           name_long="Time between first flower and first pod",
                           units="photothermal days",
                           default=8)
    flsd = PsimsFloatField(name="fl-sd",
                           name_long="Time between first flower and first seed",
                           units="photothermal days",
                           default=15)
    sdpm = PsimsFloatField(name="sd-pm",
                           name_long="Time between first seed and physiological maturity",
                           units="photothermal days",
                           default=34)
    fllf = PsimsFloatField(name="fl-lf",
                           name_long="Time between first flower and end of leaf expansion",
                           units="photothermal days",
                           default=75)
    lfmax = PsimsFloatField(name="lfmax",
                            name_long="Maximum leaf photosynthesis rate at 30 C, 350 vpm CO2, and high light",
                            units="mg CO2/m2-s",
                            default=1.1)
    slavr = PsimsFloatField(name="slavr",
                            name_long="Specific leaf area of cultivar under standard growth conditions",
                            units="cm2/g",
                            default=170)
    sizlf = PsimsFloatField(name="sizlf",
                            name_long="Maximum size of full leaf (three leaflets)",
                            units="cm2",
                            default=300)
    xfrt = PsimsFloatField(name="xfrt",
                           name_long="Maximum fraction of daily growth that is partitioned to seed + shell",
                           units="fraction",
                           default=0.61)
    wtpsd = PsimsFloatField(name="wtpsd",
                            name_long="Maximum weight per seed",
                            units="g",
                            default=0.18)
    sfdur = PsimsFloatField(name="sfdur",
                            name_long="Seed filling duration for pod cohort at standard growth conditions",
                            units="photothermal days",
                            default=35)
    sdpdv = PsimsFloatField(name="sdpdv",
                            name_long="Time required for cultivar to reach final pod load under optimal conditions",
                            units="photothermal days",
                            default=27)
    podur = PsimsFloatField(name="podur",
                            name_long="Time required for cultivar to reach final pod load under optimal conditions",
                            units="photothermal days",
                            default=12)
    thrsh = PsimsFloatField(name="thrsh",
                            name_long="Threshing percentage. The maximum ratio of (seed/(seed+shell)) at maturity. "
                                      "Causes seeds to stop growing as their dry weight increases until the shells "
                                      "are filled in a cohort",
                            units="percent",
                            default=70)
    sdpro = PsimsFloatField(name="sdpro",
                            name_long="Fraction protein in seeds",
                            units="g(protein)/g(seed)",
                            default=0.153)
    sdlip = PsimsFloatField(name="sdlip",
                            name_long="Fraction oil in seeds",
                            units="g(oil)/g(seed)",
                            default=0.12)

    # ecotype parameters
    THVAR = PsimsIntegerField(name="THVAR",
                              name_long="Minimum rate of reproductive development under short days and optimal "
                                        "temperature",
                              units="rate",
                              default=0)
    PLEM = PsimsIntegerField(name="PL-EM",
                             name_long="Time between planting and emergence (V0)",
                             units="thermal days",
                             default=4)
    EMV1 = PsimsIntegerField(name="EM-V1",
                             name_long="Time required from emergence to first true leaf (V1)",
                             units="thermal days",
                             default=4)
    V1JU = PsimsIntegerField(name="V1-JU",
                             name_long="Time required from first true leaf to end of juvenile phase",
                             units="thermal days",
                             default=0)
    JUR0 = PsimsIntegerField(name="JU-R0",
                             name_long="Time required for floral induction, equal to the minimum number of days for "
                                       "floral induction under optimal temperature and daylengths",
                             units="photothermal days",
                             default=0)
    PM09 = PsimsDecimalField(name="PM09",
                             name_long="Proportion of time between first seed and physiological maturity that the "
                                       "last seed can be formed",
                             units="ratio",
                             default=0.9)
    LNGSH = PsimsIntegerField(name="LNGSH",
                              name_long="Time required for growth of individual shells",
                              units="photothermal days",
                              default=10)
    R7R8 = PsimsIntegerField(name="R7-R8",
                             name_long="Time between physiological (R7) and harvest maturity (R8)",
                             units="days",
                             default=10)
    FLVS = PsimsIntegerField(name="FL-VS",
                             name_long="Time from first flower to last leaf on main stem",
                             units="photothermal days",
                             default=75)
    TRIFL = PsimsDecimalField(name="TRIFL",
                              name_long="Rate of appearance of leaves on the mainstem",
                              units="leaves per thermal day",
                              default=0.2)
    OPTBI = PsimsIntegerField(name="OPTBI",
                              name_long="Minimum daily temperature above which there is no effect on  slowing normal "
                                        "development toward flowering",
                              units="c",
                              default=20)


class BarleyParameters(models.Model):
    p1v = PsimsFloatField(name="p1v",
                          name_long="Optimum vernalizing temperature",
                          units="days",
                          default=0)
    p1d = PsimsFloatField(name="p1d",
                          name_long="Photoperiod response",
                          units="% reduction in rate/10 h drop in pp",
                          default=40)
    p5 = PsimsFloatField(name="p5",
                         name_long="Grain filling (excluding lag) phase duration",
                         units="C degree days",
                         default=500)
    g1 = PsimsFloatField(name="g1",
                         name_long="Kernel number per unit canopy weight at anthesis",
                         units="#/g",
                         default=20)
    g2 = PsimsFloatField(name="g2",
                         name_long="Standard kernel size under optimum conditions",
                         units="mg",
                         default=52)
    g3 = PsimsFloatField(name="g3",
                         name_long="Standard, non-stressed mature tiller wt (incl grain)",
                         units="g dry weight",
                         default=1.5)
    phint = PsimsFloatField(name="phint",
                            name_long="Interval between successive leaf tip appearances",
                            units="C degree days",
                            default=64)
    gnmn = PsimsFloatField(name="GN%MN",
                           name_long="Minimum grain N",
                           units="%",
                           default=0)
    gns = PsimsFloatField(name="GN%S",
                          name_long="Standard grain N",
                          units="%",
                          default=3)
    htstd = PsimsFloatField(name="HTSTD",
                            name_long="Standard canopy height",
                            units="cm",
                            default=100)
    la1s = PsimsFloatField(name="LA1S",
                           name_long="Area of standard first leaf",
                           units="cm2",
                           default=5)
    p1 = PsimsFloatField(name="p1",
                         name_long="Duration of phase end juvenile to terminal spikelet",
                         units="C degree days",
                         default=200)
    p2 = PsimsFloatField(name="p2",
                         name_long="Duration of phase terminal spikelet to end leaf growth",
                         units="C degree days",
                         default=200)
    p2fr1 = PsimsFloatField(name="p2fr1",
                            name_long="Duration of phase terminal spikelet to jointing",
                            units="Fraction of p2",
                            default=0.6)
    p3 = PsimsFloatField(name="p3",
                         name_long="Duration of phase end leaf growth to end spike growth",
                         units="C degree days",
                         default=200)
    p4 = PsimsFloatField(name="p4",
                         name_long="Duration of phase end spike growth to end grain fill lag",
                         units="C degree days",
                         default=500)
    p4fr1 = PsimsFloatField(name="p4fr1",
                            name_long="Duration of phase end spike growth to anthesis",
                            units="fraction of p4",
                            default=0.25)
    p4fr2 = PsimsFloatField(name="p4fr2",
                            name_long="Duration of phase anthesis start to anthesis end",
                            units="Fraction of p4",
                            default=0.1)
    rdgs = PsimsFloatField(name="RDGS",
                           name_long="Root depth growth rate,early phase",
                           units="cm/day",
                           default=3)
    rss = PsimsFloatField(name="RS%S",
                          name_long="Reserves part of assimilates going to stem",
                          units="%",
                          default=30)
    slas = PsimsFloatField(name="SLAS",
                           name_long="Specific leaf area,standard first leaf",
                           units="cm2/g",
                           default=400)
    tils = PsimsFloatField(name="TIL#S",
                           name_long="Tiller production starts",
                           units="leaf #",
                           default=3.5)


class CanolaParameters(models.Model):
    # cultivar parameters
    csdl = PsimsFloatField(name="csdl",
                           name_long="Critical Short Day Length below which reproductive development progresses with no"
                                     "daylength effect (for shortday plants)",
                           units="hour",
                           default=24)
    ppsen = PsimsFloatField(name="ppsen",
                            name_long="Slope of the relative response of development to photoperiod with time (positive"
                                      "for shortday plants)",
                            units="slope",
                            default=-0.03)
    emfl = PsimsFloatField(name="em-fl",
                           name_long="Time between plant emergence and flower appearance",
                           units="photothermal days",
                           default=29)
    flsh = PsimsFloatField(name="fl-sh",
                           name_long="Time between first flower and first pod",
                           units="photothermal days",
                           default=15)
    flsd = PsimsFloatField(name="fl-sd",
                           name_long="Time between first flower and first seed",
                           units="photothermal days",
                           default=30.5)
    sdpm = PsimsFloatField(name="sd-pm",
                           name_long="Time between first seed and physiological maturity",
                           units="photothermal days",
                           default=25)
    fllf = PsimsFloatField(name="fl-lf",
                           name_long="Time between first flower and end of leaf expansion",
                           units="photothermal days",
                           default=3)
    lfmax = PsimsFloatField(name="lfmax",
                            name_long="Maximum leaf photosynthesis rate at 30 C, 350 vpm CO2, and high light",
                            units="mg CO2/m2-s",
                            default=1.03)
    slavr = PsimsFloatField(name="slavr",
                            name_long=" Specific leaf area of cultivar under standard growth conditions",
                            units="cm2/g",
                            default=250)
    sizlf = PsimsFloatField(name="sizlf",
                            name_long="Maximum size of full leaf (three leaflets)",
                            units="cm2",
                            default=100)
    xfrt = PsimsFloatField(name="xfrt",
                           name_long="Maximum fraction of daily growth that is partitioned to seed + shell",
                           units="fraction",
                           default=1)
    wtpsd = PsimsFloatField(name="wtpsd",
                            name_long="Maximum weight per seed",
                            units="g",
                            default=0.003)
    sfdur = PsimsFloatField(name="sfdur",
                            name_long="Seed filling duration for pod cohort at standard growth conditions",
                            units="photothermal days",
                            default=20)
    sdpdv = PsimsFloatField(name="sdpdv",
                            name_long="Average seed per pod under standard growing conditions",
                            units="#/pod",
                            default=22)
    podur = PsimsFloatField(name="podur",
                            name_long="Time required for cultivar to reach final pod load under optimal conditions",
                            units="photothermal days",
                            default=10)

    # ecotype parameters
    thrsh = PsimsFloatField(name="thrsh",
                            name_long="Threshing percentage. The maximum ratio of (seed/(seed+shell))",
                            units="percentage",
                            default=81)
    sdpro = PsimsFloatField(name="sdpro",
                            name_long="Fraction protein in seeds (g(protein)/g(seed))",
                            units="fraction",
                            default=0.230)

    sdlip = PsimsFloatField(name="sdlip",
                            name_long="Fraction oil in seeds",
                            units="g(oil)/g(seed)",
                            default=0.480)
    mg = PsimsFloatField(name="mg",
                         name_long="Maturity group number for this ecotype",
                         units="number",
                         default=1)
    tm = PsimsFloatField(name="tm",
                         name_long="Indicator of temperature adaptation",
                         units="number",
                         default=1)
    thvar = PsimsFloatField(name="thvar",
                            name_long="Minimum rate of reproductive development under long days and optimal temperature",
                            units="rate",
                            default=0)
    plem = PsimsFloatField(name="pl-em",
                           name_long="Time between planting and emergence",
                           units="thermal days",
                           default=3.6)
    emv1 = PsimsFloatField(name="em-v1",
                           name_long="Time required from emergence to first true leaf",
                           units="thermal days",
                           default=6)
    v1ju = PsimsFloatField(name="v1-ju",
                           name_long="Time required from first true leaf to end of juvenile phase",
                           units="thermal days",
                           default=0)
    jur0 = PsimsFloatField(name="ju-r0",
                           name_long="Time required for floral induction, equal to the minimum number of days for "
                                     "floral induction under optimal temperature and daylengths",
                           units="thermal days",
                           default=5)
    pm06 = PsimsFloatField(name="pm06",
                           name_long="Proportion of time between first flower and first pod for first peg",
                           units="peanut only",
                           default=0)
    pm09 = PsimsFloatField(name="pm09",
                           name_long="Proportion of time between first seed and physiological maturity that the last "
                                     "seed can be formed",
                           units="proportion",
                           default=0.35)
    lngsh = PsimsFloatField(name="lngsh",
                            name_long="Time required for growth of individual shells",
                            units="photothermal days",
                            default=10)
    r7r8 = PsimsFloatField(name="r7-r8",
                           name_long="Time between physiological (R7) and harvest maturity (R8)",
                           units="days",
                           default=3)
    flvs = PsimsFloatField(name="fl-vs",
                           name_long="Time from first flower to last leaf on main stem",
                           units="photothermal days",
                           default=0)
    trifl = PsimsFloatField(name="trifl",
                            name_long="Rate of appearance of leaves on the mainstem",
                            units="leaves per thermal day",
                            default=0.35)
    rwdth = PsimsFloatField(name="rwdth",
                            name_long="Relative width of this ecotype in comparison to the standard idth per node "
                                      "(YVSWH) defined in the species file",
                            units="*.SPE",
                            default=1)
    rhght = PsimsFloatField(name="rhght",
                            name_long="Relative height of this ecotype in comparison to the standard height per node "
                                      "(YVSHT) defined in the species file",
                            units="*.SPE",
                            default=1.5)
    r1ppo = PsimsFloatField(name="r1ppo",
                            name_long="Increase in daylength sensitivity after R1 (CSDVAR and CLDVAR both decrease with"
                                      " the same amount)",
                            units="h",
                            default=0)
    optbi = PsimsFloatField(name="optbi",
                            name_long="Minimum daily temperature above which there is no effect on slowing normal "
                                      "development toward flowering",
                            units="oC",
                            default=0)
    slobi = PsimsFloatField(name="slobi",
                            name_long="Slope of relationship reducing progress toward flowering if TMIN for the day is "
                                      "less than OPTBI",
                            units="slope",
                            default=0)


class ChickpeaParameters(models.Model):

    # cultivar parameters
    csdl = PsimsFloatField(name="csdl",
                           name_long="Critical Short Day Length below which reproductive development progresses "
                                     "WITH daylength effect for longday plants",
                           units="hours",
                           default=11)
    ppsen = PsimsFloatField(name="ppsen",
                            name_long="Slope of the relative response of development to photoperiod with time (negative for longday plants)",
                            units="1/hour",
                            default=-0.143)
    emfl = PsimsFloatField(name="em-fl",
                           name_long="Time between plant emergence and flower appearance",
                           units="photothermal days",
                           default=32)
    flsh = PsimsFloatField(name="fl-sh",
                           name_long="Time between first flower and first pod",
                           units="photothermal days",
                           default=6)
    flsd = PsimsFloatField(name="fl-sd",
                           name_long="Time between first flower and first seed",
                           units="photothermal days",
                           default=19.5)
    sdpm = PsimsFloatField(name="sd-pm",
                           name_long="Time between first seed and physiological maturity",
                           units="photothermal days",
                           default=31.5)
    fllf = PsimsFloatField(name="fl-lf",
                           name_long="Time between first flower and end of leaf expansion",
                           units="photothermal days",
                           default=42)
    lfmax = PsimsFloatField(name="lfmax",
                            name_long="Maximum leaf photosynthesis rate at 30 C, 350 vpm CO2, and high light",
                            units="mg CO2/m2-s",
                            default=0.95)
    slavr = PsimsFloatField(name="slavr",
                            name_long="Specific leaf area of cultivar under standard growth conditions",
                            units="cm2/g",
                            default=200)
    sizlf = PsimsFloatField(name="sizlf",
                            name_long="Maximum size of full leaf (three leaflets)",
                            units="cm2",
                            default=10)
    xfrt = PsimsFloatField(name="xfrt",
                           name_long="Maximum fraction of daily growth that is partitioned to seed + shell",
                           units="fraction",
                           default=0.96)
    wtpsd = PsimsFloatField(name="wtpsd",
                            name_long="Maximum weight per seed",
                            units="g",
                            default=0.23)
    sfdur = PsimsFloatField(name="sfdur",
                            name_long="Seed filling duration for pod cohort at standard growth conditions",
                            units="photothermal days",
                            default=22)
    sdpdv = PsimsFloatField(name="sdpdv",
                            name_long="Average seed per pod under standard growing conditions",
                            units="#/pod",
                            default=1.2)
    podur = PsimsFloatField(name="podur",
                            name_long="Time required for cultivar to reach final pod load under optimal conditions",
                            units="photothermal days",
                            default=18)
    thrsh = PsimsFloatField(name="thrsh",
                            name_long="The maximum ratio of (seed/(seed+shell)) at maturity. Causes seed to stop "
                                      "growing as their dry weights increase until shells are filled in a cohort",
                            units="threshing percentage",
                            default=85)
    sdpro = PsimsFloatField(name="sdpro",
                            name_long="Fraction protein in seeds",
                            units="Fraction protein in seeds",
                            default=0.216)
    sdlip = PsimsFloatField(name="sdlip",
                            name_long="Fraction oil in seeds",
                            units="g(oil)/g(seed)",
                            default=0.48)

    # ecotype parameters
    THVAR = PsimsDecimalField(name="THVAR",
                              name_long="Minimum rate of reproductive development under short days and optimal "
                                        "temperature",
                              units="rate",
                              default=0)
    PLEM = PsimsDecimalField(name="PL-EM",
                             name_long="Time between planting and emergence (V0)",
                             units="thermal days",
                             default=2)
    EMV1 = PsimsDecimalField(name="EM-V1",
                             name_long="Time between planting and emergence (V1)",
                             units="thermal days",
                             default=1.5)
    V1JU = PsimsDecimalField(name="V1-JU",
                             name_long="Time required from first true leaf to end of juvenile phase",
                             units="thermal days",
                             default=0)
    JURO = PsimsDecimalField(name="JU-R0",
                             name_long="Time required for floral induction, equal to the minimum number of days for "
                                       "floral induction",
                             units="photothermal days",
                             default=5)
    PM09 = PsimsDecimalField(name="PM-09",
                             name_long="Proportion of time between first seed and physiological maturity that the "
                                       "last seed can be formed",
                             units="propportion",
                             default=0.2)
    LNGSH = PsimsDecimalField(name="LNGSH",
                              name_long="Time required for growth of individual shells",
                              units="photothermal days",
                              default=7)
    R7R8 = PsimsIntegerField(name="R7-R8",
                             name_long="Time between physiological and harvest maturity",
                             units="days",
                             default=8)
    FLVS = PsimsDecimalField(name="FL-VS",
                             name_long="Time from first flower to last leaf on main stem",
                             units="photothermal days",
                             default=19)
    TRIFL = PsimsDecimalField(name="TRIFL",
                              name_long="Rate of appearance of leaves on the mainstem",
                              units="leaves per thermal day",
                              default=0.6)
    OPTBI = PsimsDecimalField(name="OPTBI",
                              name_long="Minimum daily temperature above which there is no effect on slowing normal "
                                        "development toward flowering",
                              units="C",
                              default=0)


class SorghumParameters(models.Model):
    # cultivar parameters
    p1 = PsimsFloatField(name="p1",
                         name_long="Thermal time from seedling emergence to the end of the  juvenile phase ("
                                     "expressed in degree days above TBASE during which the plant is not responsive "
                                     "to changes in photoperiod",
                         units="degree days",
                         default=360)
    p2 = PsimsFloatField(name="p2",
                         name_long="Thermal time from the end of the juvenile stage to tassel initiation under "
                                     "short days",
                         units="degree days",
                         default=102)
    p2o = PsimsFloatField(name="p2o",
                          name_long="Critical photoperiod or the longest day length (in hours) at which development "
                                    "occurs at a maximum rate. At values higher than this, the rate of development "
                                    "is reduced",
                          units="hours",
                          default=14,
                          validators=[MaxValueValidator(24)])
    panth = PsimsFloatField(name="panth",
                            name_long="Thermal time from the end of tassel initiation to anthesis",
                            units="degree days above TBASE",
                            default=617.5)
    p2r = PsimsFloatField(name="p2r",
                          name_long="Extent to which phasic development leading to panicle"
                                    "initiation is delayed for each hour"
                                    "increase in photoperiod above P2O",
                          units="degree days",
                          default=30)
    p3 = PsimsFloatField(name="p3",
                         name_long="Thermal time from to end of flag leaf expansion to anthesis",
                         units="degree days above TBASE",
                         default=152.5)
    p4 = PsimsFloatField(name="p4",
                         name_long="Thermal time from anthesis to beginning grain filling",
                         units="degree days above TBASE",
                         default=81.5)
    p5 = PsimsFloatField(name="p5",
                         name_long="Thermal time from beginning of grain filling to physiological maturity",
                         units="degree days above TBASE",
                         default=540)
    phint = PsimsFloatField(name="phint",
                            name_long="Phylochron interval; the interval in thermal time between successive leaf "
                                      "tip appearances",
                            units="degree days",
                            default=49)
    g1 = PsimsFloatField(name="g1",
                         name_long="Scaler for relative leaf size",
                         units="ratio",
                         default=3)
    g2 = PsimsFloatField(name="g2",
                         name_long="Scaler for partitioning of assimilates to the panicle",
                         units="fraction",
                         default=6)
    tbase = PsimsDecimalField(name="tbawe",
                              name_long="Base temperature below which no development occurs",
                              units="C",
                              default=8)

    # ecotype parameters
    topt = PsimsDecimalField(name="topt",
                             name_long="Temperature at which maximum development occurs for vegetative stages",
                             units="C",
                             default=34)
    ropt = PsimsDecimalField(name="ropt",
                             name_long="Temperature at which maximum development occurs for reproductive stages",
                             units="C",
                             default=34)
    gdde = PsimsDecimalField(name="gdde",
                             name_long="Growing degree days per cm seed depth required for emergence",
                             units="degree days/cm",
                             default=6)
    rue = PsimsDecimalField(name="rue",
                            name_long="Radiation use efficiency",
                            units="g plant dry matter/MJ PAR",
                            default=3.2)
    kcan = PsimsDecimalField(name="kcan",
                             name_long="Canopy light extinction coefficient for daily PAR",
                             units="fraction",
                             default=0.85)
    stpc = PsimsDecimalField(name="stpc",
                             name_long="Partitioning to stem growth as a fraction of potential leaf growth",
                             units="fraction",
                             default=0.1)
    rtpc = PsimsDecimalField(name="rtpc",
                             name_long="Partitioning to root growth as a fraction of available carbohydrates",
                             units="fraction",
                             default=0.25)
    tilfc = PsimsDecimalField(name="tilfc",
                              name_long="Tillering factor",
                              units="0 to 1, 0.0=no tillering, 1.0=full tillering",
                              default=1)


class CassavaParameters(models.Model):
    B01ND = PsimsIntegerField(name="B01ND",
                              name_long="Duration from branch 0 to branch 1",
                              units="thermal units",
                              default=380)
    B12ND = PsimsIntegerField(name="B12ND",
                              name_long="Duration from branch 1 to branch 2",
                              units="thermal units",
                              default=410)
    BR1FX = PsimsDecimalField(name="BR1FX",
                              name_long="Branch number per fork at fork 1",
                              units="number",
                              default=2.1)
    BR2FX = PsimsDecimalField(name="BR2FX",
                              name_long="Branch number per fork at fork 2",
                              units="number",
                              default=3.1)
    BR3FX = PsimsDecimalField(name="BR3FX",
                              name_long="Branch number per fork at fork 3",
                              units="number",
                              default=2.7)
    BR4FX = PsimsDecimalField(name="BR4FX",
                              name_long="Branch number per fork at fork 4",
                              units="number",
                              default=1)
    LAXS = PsimsDecimalField(name="LAXS",
                             name_long="Maximum area/leaf when crop growing without stress",
                             units="cm2",
                             default=550)
    SLAS = PsimsDecimalField(name="SLAS",
                             name_long="Specific leaf lamina area when crop growing without stress",
                             units="cm2/g",
                             default=220)
    LLIFA = PsimsIntegerField(name="LLIFA",
                              name_long="Leaf life,from full expansion to start senescence",
                              units="thermal units",
                              default=900)
    LNSLP = PsimsDecimalField(name="LNSLP",
                              name_long="Slope for leaf production",
                              units="rate - 0.8 low rate, 1.0 medium rate, 1.2 high rate",
                              default=1.1)
    NODWT = PsimsDecimalField(name="NODWT",
                              name_long="Node weight for the first stem of the shoot before branching at 3400 ˚Cd",
                              units="g",
                              default=6)
    NODLT = PsimsDecimalField(name="NODLT",
                              name_long="Mean internode length for the first stem of the shoot before branching when "
                                        "is lignified",
                              units="cm",
                              default=2)
    PARUE = PsimsDecimalField(name="PARUE",
                              name_long="PAR conversion factor, standard",
                              units="g dry matter/MJ",
                              default=2.8)
    TBLSZ = PsimsDecimalField(name="TBLSZ",
                              name_long="Base temperature for leaf development",
                              units="C",
                              default=12)
    SRNS = PsimsDecimalField(name="SRN%S",
                             name_long="Storage root standard N concentration",
                             units="% dry matter",
                             default=0.65)
    KCAN = PsimsDecimalField(name="KCAN",
                             name_long="PAR extinction coefficient",
                             units="#",
                             default=0.65)
    PGERM = PsimsDecimalField(name="PGERM",
                              name_long="Germination duration",
                              units="thermal units",
                              default=120)
