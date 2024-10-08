from django.urls import path
from .admin import admin_site # import custom admin site
from benchmarks.views import TopologyTable, ManufacturerTable, TechnologyTable, ProcessorTable, GateSetTable, GateTable, GateSetMembershipTable
from benchmarks.views import SystemTable, CalibrationTable,  SolverTable, PerformanceMetricTable
from benchmarks.views import GraphTable, ProblemTable, PerformanceReportTable
from benchmarks.views import Performance, ProblemInstanceList, SystemCali, ProcessorList, GateList
from benchmarks.views import CompilationToolTable, CompilationAlgorithmnTable, CompilationStepTable, PerformanceValueTable, ProblemInstanceTable
from benchmarks.views import customize, manytable, Value, Value2
from . import views
app_name = 'benchmarks'  # creates a namespace for this app
urlpatterns = [
    path('', views.index, name='index'),
    path('people/', views.people, name='people'),
    path('admin/', admin_site.urls),
    path('algorithm-and-application/', views.algoandapp),
    path('reference/', views.ref),

    path('report/', Performance),
    path('instance/', ProblemInstanceList),
    path('system/', SystemCali),
    path('processor/', ProcessorList),
    path('gate/', GateList),
    path('manufacturers/', ManufacturerTable.as_view()),
    path('technologies/', TechnologyTable.as_view()),
    path('solvers/', SolverTable.as_view()),
    path('performancemetrics/', PerformanceMetricTable.as_view()),
    path('topologies/', TopologyTable.as_view()),
    path('processors/', ProcessorTable.as_view()),
    path('gatesets/', GateSetTable.as_view()),
    path('gates/', GateTable.as_view()),
    path('gatesetmemberships/', GateSetMembershipTable.as_view()),
    path('systems/', SystemTable.as_view()),
    path('calibrations/', CalibrationTable.as_view()),
    path('graphs/', GraphTable.as_view()),
    path('problems/', ProblemTable.as_view()),
    path('performancereports/', PerformanceReportTable.as_view()),
    path('compilationtools/', CompilationToolTable.as_view()),
    path('compilationalgorithmns/', CompilationAlgorithmnTable.as_view()),
    path('compilationsteps/', CompilationStepTable.as_view()),
    path('performancevalues/', PerformanceValueTable.as_view()),
    path('probleminstances/', ProblemInstanceTable.as_view()),

    path('joined-performance/', Performance, name='joined_performance'),
    path('joined-problems/', ProblemInstanceList, name='joined_performance'),
    path('joined-system/', SystemCali, name='joined_performance'),
    path('joined-processor/', ProcessorList, name='joined_performance'),
    path('joined-gate/', GateList, name='joined_performance'),
    path('value/', Value, name='joined_performance'),
    path('value2/', Value2, name='joined_performance'),

    path('customize/', customize, name='customize'),
    path('ManyTable/', manytable, name='manytable'),
]
