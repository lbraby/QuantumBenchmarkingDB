from django.urls import path
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from .views import dataupload

# import models
from .models import Topology, Manufacturer, Technology, Processor
from .models import GateSet, Gate, GateSetMembership
from .models import System, Calibration
from .models import Solver, PerformanceMetric, Graph, Problem, PerformanceReport
from .models import CompilationTool, CompilationAlgorithmn, CompilationStep, PerformanceValue, ProblemInstance
from .models import ErrorLog

# customize admin site
class AdminSiteBench(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dataupload/', self.admin_view(dataupload), name='custom_admin_view'),
        ]
        return custom_urls + urls
    
    index_template = "admin/index.html"

admin_site = AdminSiteBench(name='admin')

# Register your models here.
admin_site.register(Topology)
admin_site.register(Manufacturer)
admin_site.register(Technology)
admin_site.register(Processor)
admin_site.register(GateSet)
admin_site.register(Gate)
admin_site.register(GateSetMembership)
admin_site.register(System)
admin_site.register(Calibration)
admin_site.register(Solver)
admin_site.register(PerformanceMetric)
admin_site.register(Graph)
admin_site.register(Problem)
admin_site.register(PerformanceReport)
admin_site.register(CompilationTool)
admin_site.register(CompilationAlgorithmn)
admin_site.register(CompilationStep)
admin_site.register(PerformanceValue)
admin_site.register(ProblemInstance)
admin_site.register(ErrorLog)
