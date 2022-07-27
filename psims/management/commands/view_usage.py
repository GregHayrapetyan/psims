from django.core.management.base import BaseCommand
from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from psims.models import PsimsOutput
import pandas as pd


class Command(BaseCommand):

    @staticmethod
    def dateify(d):
        if isinstance(d, str):
            return datetime.strptime(d, '%Y-%m-%d')
        return d

    def add_arguments(self, parser):
        start = datetime.now(timezone.utc) - timedelta(days=15)
        end = datetime.now(timezone.utc) - timedelta(days=1)
        parser.add_argument('--start', required=False, default=start, help="Start date in yyyy-mm-dd format")
        parser.add_argument('--end', required=False, default=end, help="End date in yyyy-mm-dd format")

    def handle(self, *args, **options):
        start = self.dateify(options['start'])
        end = self.dateify(options['end'])
        outputs = PsimsOutput.objects.filter(created_at__gte=start, created_at__lt=end).values_list('created_at', 'owner__username')
        df = pd.DataFrame.from_records(outputs, columns=['Date', 'User'])
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        print(df.groupby(df['Date']).count())
        return
