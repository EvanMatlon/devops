from django.shortcuts import render
from django.http import HttpResponse
from playbook import * 
from deploy.models import Host

# Create your views here.
def index(request):
	
	return render(request,'base.html')

def task(request):
	return render(request,'task.html')

def host(request):
	hosts = Host.objects.all()
	
	return render(request,'host.html',{'hosts':hosts})

def playbook(request):
	id = request.GET['a']
	role = request.GET['b']
	exe_group = request.GET['c']
        runner = MyRun()
        runner.run(id,role,exe_group)
        result = runner.get_results(id)
        #print result
        return HttpResponse(result,content_type='application/json')
	#print response
	#print type(result)
    	#return response
	
