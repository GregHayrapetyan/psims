from psims.models import PsimsOutput

def context_processor(request):
    if hasattr(request.user,'psims_worker'):
        worker = request.user.psims_worker
        if worker and worker.completed_worker_id and not worker.is_seen:
            worker.is_seen = True
            worker.save()
            return {'has_worker_alert': True,'completed_worker_id':worker.completed_worker_id}
    return {'has_worker_alert': False}

def GetNotifications(request):
    context = {}
    if request.user.is_authenticated:
        new= PsimsOutput.objects.filter(owner=request.user)
        isopens = []
        is_deleted = []
        print()
        for i in new:
            
            if i.is_open == False:
                isopens.append(i)
            if i.is_deleted and i.is_open == False:
                is_deleted.append(i)

        print()    
        context["isopens"] = len(isopens)
        context['isdeleted'] = len(isopens) - len(is_deleted)
    return context