import xlwt
from django.http import Http404, HttpResponseForbidden, HttpResponse, response
import redis
from celery import Celery
from psims_web_project.celery import app


def my_monitor(app):
    state = app.events.State()

    def announce_failed_tasks(event):
        state.event(event)
        # task name is sent only with -received event, and state
        # will keep track of this for us.
        task = state.tasks.get(event['uuid'])

        print('TASK FAILED: %s[%s] %s' % (
            task.name, task.uuid, task.info(),))

    with app.connection() as connection:
        recv = app.events.Receiver(connection, handlers={
                'task-failed': announce_failed_tasks,
                '*': state.event,
        })
        recv.capture(limit=None, timeout=None, wakeup=True)

        
def export_results(obj):
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
    for i in range(len(obj)):
        ws.write(i+1, 0, str(obj[i].created_at), font_style2)
        ws.write(i+1, 1, str(obj[i].location), font_style2)
        ws.write(i+1, 2, str(obj[i].crop), font_style2)
        ws.write(i+1, 3, str(obj[i].planting_day.planting_date), font_style2)
        ws.write(i+1, 4, str(obj[i].location.latitude), font_style2)
        ws.write(i+1, 5, str(obj[i].location.longitude), font_style2)
        ws.write(i+1, 6, str(obj[i].last_year), font_style2)
        ws.write(i+1, 7, str(obj[i].last_year), font_style2)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=User_inputs.xls'
    wb.save(response)
    print(321)
    return response

if __name__ == '__main__':
    print(my_monitor(app))




