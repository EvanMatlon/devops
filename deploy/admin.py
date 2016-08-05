from django.contrib import admin
from deploy.models import Host

# Register your models here.

class HostAdmin(admin.ModelAdmin):
	list_display = ('ip','hostname','group','create_time')


admin.site.register(Host,HostAdmin)
