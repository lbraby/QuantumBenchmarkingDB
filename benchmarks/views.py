from django.shortcuts import render
from .forms import PerformanceReportForm, ProblemForm
from django_tables2 import SingleTableView
from django.contrib.admin.views.decorators import staff_member_required
from .models import Topology, Manufacturer, Technology, Processor, GateSet, Gate, GateSetMembership
from .models import System, Calibration, Solver, PerformanceMetric
from .models import Graph, Problem, PerformanceReport
from .models import CompilationTool, CompilationAlgorithmn, CompilationStep, PerformanceValue, ProblemInstance
from .tables import ManufacturerTable, TechnologyTable, TopologyTable, ProcessorTable, GateSetTable, GateTable, GateSetMembershipTable, SystemTable, CalibrationTable, GraphTable, ProblemTable, PerformanceReportTable, SolverTable,PerformanceMetricTable
from .tables import CompilationToolTable, CompilationAlgorithmnTable, CompilationStepTable, PerformanceValueTable, ProblemInstanceTable
from django.db import connection
from django.http import HttpRequest
from .models import ErrorLog
from .graph import graph
import os
from .csvupload import handle_problem_upload, handle_performance_report_upload

# Create your views here.
def index(request):
    return render(request, 'benchmarks/index.html')
def people(request):
    return render(request, 'benchmarks/people.html')
def algoandapp(request):
    return render(request, 'benchmarks/algoandapp.html')
def ref(request):
    return render(request, 'benchmarks/reference.html')

class CompilationToolTable(SingleTableView):
    model = CompilationTool
    table_class = CompilationToolTable
    template_name = "benchmarks/table.html"

class CompilationAlgorithmnTable(SingleTableView):
    model = Manufacturer
    table_class = CompilationAlgorithmnTable
    template_name = "benchmarks/table.html"

class CompilationStepTable(SingleTableView):
    model = CompilationStep
    table_class = CompilationStepTable
    template_name = "benchmarks/table.html"

class PerformanceValueTable(SingleTableView):
    model = PerformanceValue
    table_class = PerformanceValueTable
    template_name = "benchmarks/table.html"

class ProblemInstanceTable(SingleTableView):
    model = ProblemInstance
    table_class = ProblemInstanceTable
    template_name = "benchmarks/table.html"

class ManufacturerTable(SingleTableView):
    model = Manufacturer
    table_class = ManufacturerTable
    template_name = "benchmarks/table.html"

class TechnologyTable(SingleTableView):
    model = Technology
    table_class= TechnologyTable
    template_name = "benchmarks/table.html"

class SolverTable(SingleTableView):
    model = Solver
    table_class = SolverTable
    template_name = "benchmarks/table.html"

class PerformanceMetricTable(SingleTableView):
    model = PerformanceMetric
    table_class = PerformanceMetricTable
    template_name = "benchmarks/table.html"


class TopologyTable(SingleTableView):
    model = Topology
    table_class= TopologyTable
    template_name = "benchmarks/table.html"

class ProcessorTable(SingleTableView):
    model = Processor
    table_class = ProcessorTable
    template_name = "benchmarks/table.html"

class GateSetTable(SingleTableView):
    model = GateSet
    table_class = GateSetTable
    template_name = "benchmarks/table.html"

class GateTable(SingleTableView):
    model = Gate
    table_class = GateTable
    template_name = "benchmarks/table.html"

class GateSetMembershipTable(SingleTableView):
    model = GateSetMembership
    table_class= GateSetMembershipTable
    template_name = "benchmarks/table.html"

class SystemTable(SingleTableView):
    model = System
    table_class = SystemTable
    template_name = "benchmarks/table.html"

class CalibrationTable(SingleTableView):
    model = Calibration
    table_class = CalibrationTable
    template_name = "benchmarks/table.html"

class GraphTable(SingleTableView):
    model = Graph
    table_class = GraphTable
    template_name = "benchmarks/table.html"

class ProblemTable(SingleTableView):
    model = Problem
    table_class = ProblemTable
    template_name = "benchmarks/table.html"

class PerformanceReportTable(SingleTableView):
    model = PerformanceReport
    table_class= PerformanceReportTable
    template_name = "benchmarks/table.html"

def Performance(request):
    extrastringcreate = '''
        CREATE TEMPORARY TABLE temp_metric (
        performance_report_id INTEGER,
        combined TEXT,
        chosen TEXT)'''

    extrastringinsert = '''INSERT INTO temp_metric (performance_report_id, combined, chosen)
    SELECT performance_report_id,
    string_agg(value || ' ' || name, ', ') AS combined,
    MAX(CASE 
        WHEN name = 'Modularity Ratio (current/Best)' THEN value
            ELSE NULL
        END) AS chosen
    FROM benchmarks_performancevalue
    full join benchmarks_performancemetric on benchmarks_performancemetric.id = benchmarks_performancevalue.metric_id
    group by performance_report_id
    '''
    with connection.cursor() as cursor:
        cursor.execute(extrastringcreate)
        cursor.execute(extrastringinsert)
        cursor.execute('''SELECT a.id,
        a.qubo_var_count,
        a.qubo_quad_term_count,
        a.qubit_count,
        a.rcs,
        a.mean_chain_length,
        a.max_chain_length,
        a.num_runs,
        b.name,
        temp_metric.combined,
        temp_metric.chosen,
        e.version,
        f.name,
        g.name
         FROM benchmarks_PerformanceReport as a 
        left join benchmarks_solver as b on a.solver_id =b.id
        left join benchmarks_performanceValue as c on c.performance_report_id = a.id 
        left join benchmarks_performanceMetric as d on c.metric_id= d.id
        left join benchmarks_compilationstep as e on e.performance_report_id = a.id
        left join benchmarks_compilationAlgorithmn as f on f.id= e.compilation_Algorithmn_id
        left join benchmarks_compilationTool as g on g.id = e.compilation_tool_id
        full join temp_metric on a.id = temp_metric.performance_report_id''')
        joined_results = cursor.fetchall()

    # Check if any results were fetched
    if not joined_results:
        print("No results found")

    columns = [col[0] for col in cursor.description]
    context = {
        'joined_results': joined_results,  # Ensure this matches your template
        'columns': columns
    }
    return render(request, 'benchmarks/Report.html', context)

def ProblemInstanceList(request):
    
    with connection.cursor() as cursor:
        cursor.execute('''SELECT a.id,
        a.graph_size,
        b.name,
        c.name FROM benchmarks_ProblemInstance as a 
        left join benchmarks_graph as b on a.graph_id =b.id
        left join benchmarks_problem as c on c.id = a.problem_id
        ''')
        joined_results = cursor.fetchall()

    # Check if any results were fetched
    if not joined_results:
        print("No results found")

    columns = [col[0] for col in cursor.description]
    context = {
        'joined_results': joined_results,  # Ensure this matches your template
        'columns': columns
    }
    return render(request, 'benchmarks/ProblemInstance.html', context)


def SystemCali(request):
    
    with connection.cursor() as cursor:
        cursor.execute('''SELECT * FROM benchmarks_system as a 
        left join benchmarks_calibration as b on a.id= b.system_id
        ''')
        joined_results = cursor.fetchall()

    # Check if any results were fetched
    if not joined_results:
        print("No results found")

    columns = [col[0] for col in cursor.description]
    context = {
        'joined_results': joined_results,  # Ensure this matches your template
        'columns': columns
    }
    return render(request, 'benchmarks/System.html', context)



def ProcessorList(request):
    
    with connection.cursor() as cursor:
        cursor.execute('''SELECT * FROM benchmarks_Processor as a 
        left join benchmarks_manufacturer as b on a.manufacturer_id =b.id
        left join benchmarks_technology as c on c.id = a.technology_id
        left join benchmarks_topology as d on a.topology_id=d.id
        ''')
        joined_results = cursor.fetchall()

    # Check if any results were fetched
    if not joined_results:
        print("No results found")

    columns = [col[0] for col in cursor.description]
    context = {
        'joined_results': joined_results,  # Ensure this matches your template
        'columns': columns
    }
    return render(request, 'benchmarks/Processor.html', context)

def GateList(request):
    
    with connection.cursor() as cursor:
        cursor.execute('''SELECT * FROM benchmarks_gateset as a 
        left join benchmarks_gatesetmembership as b on a.id =b.gate_set_id
        left join benchmarks_gate as c on c.id = b.gate_id
        ''')
        joined_results = cursor.fetchall()

    # Check if any results were fetched
    if not joined_results:
        print("No results found")

    columns = [col[0] for col in cursor.description]
    context = {
        'joined_results': joined_results,  # Ensure this matches your template
        'columns': columns
    }
    return render(request, 'benchmarks/Gate.html', context)

def Value(request):
    
    with connection.cursor() as cursor:
        cursor.execute('''SELECT performance_report_id,
        string_agg(value || ' ' || name, ', ') AS combined,
        MAX(CASE 
               WHEN name = 'Modularity Ratio (current/Best)' THEN value
               ELSE NULL
           END) AS Desire
        FROM benchmarks_performancevalue
        full join benchmarks_performancemetric on benchmarks_performancemetric.id = benchmarks_performancevalue.metric_id
        group by performance_report_id
        ''')
        joined_results = cursor.fetchall()

    # Check if any results were fetched
    if not joined_results:
        print("No results found")

    columns = [col[0] for col in cursor.description]
    context = {
        'joined_results': joined_results,  # Ensure this matches your template
        'columns': columns
    }
    return render(request, 'benchmarks/maintable.html', context)
def Value2(request):
    
    with connection.cursor() as cursor:
        cursor.execute('''SELECT *
        FROM benchmarks_performancevalue
        full join benchmarks_performancemetric on benchmarks_performancemetric.id = benchmarks_performancevalue.metric_id
        
        ''')
        joined_results = cursor.fetchall()

    # Check if any results were fetched
    if not joined_results:
        print("No results found")

    columns = [col[0] for col in cursor.description]
    context = {
        'joined_results': joined_results,  # Ensure this matches your template
        'columns': columns
    }
    return render(request, 'benchmarks/maintable.html', context)

def customize(request: HttpRequest):
    
    user_columns = request.GET.getlist('columns')
    user_base = request.GET.getlist('base')
    user_joins = request.GET.getlist('joins')
    user_filter= request.GET.getlist('filter')

    

    if user_base:
        base = user_base[0]
        if base == "benchmarks_performancereport":
            basetable = "benchmarks_performanceReport as a"
        elif base == "benchmarks_system":
            basetable = "benchmarks_system as b"
        elif base == "benchmarks_gateset":
            basetable = "benchmarks_gateset as c"
        elif base == "benchmarks_probleminstance":
            basetable = "benchmarks_probleminstance as d"
    else:
        basetable = "benchmarks_performanceReport as a"

    if not user_columns or "reset" in user_columns:
        user_columns = ["*"]

    filter=[]
    if user_filter:
        for index in range(0,len(user_filter)-1,2):
            if user_filter[index+1] != '':
                filter.append(user_filter[index] + " like '%" + user_filter[index+1] + "%'")
    


    join_clauses = []
    if user_joins:
        for table in user_joins:
            if basetable == "benchmarks_performanceReport as a":
                if table == "benchmarks_solver":
                    join_clauses.append("left join benchmarks_solver as e on a.solver_id = e.id")
                elif table == "benchmarks_performanceValue":
                    join_clauses.append("left join benchmarks_performanceValue as f on f.performance_report_id = a.id")
                elif table == "benchmarks_compilationstep":
                    join_clauses.append("left join benchmarks_compilationstep as g on g.performance_report_id = a.id")
                elif table == "benchmarks_system":
                    join_clauses.append("left join benchmarks_system as h on h.id = a.system_id")
                elif table == "benchmarks_probleminstance":
                    join_clauses.append("left join benchmarks_probleminstance as i on i.id = a.problem_id")
            elif basetable == "benchmarks_system as b":
                if table == "benchmarks_performancereport":
                    join_clauses.append("left join benchmarks_performancereport as j on j.system_id = b.id")
                elif table == "benchmarks_calibration":
                    join_clauses.append("left join benchmarks_calibration as k on k.system_id = b.id")
                elif table == "benchmarks_manufacturer":
                    join_clauses.append("left join benchmarks_manufacturer as l on l.id = b.manufactor_id")
                elif table == "benchmarks_processor":
                    join_clauses.append("left join benchmarks_processor as m on m.id = b.processor_id")
                elif table == "benchmarks_gateset":
                    join_clauses.append("left join benchmarks_gateset as n on n.id = b.gateset_id")
            elif basetable == "benchmarks_gateset as c":
                if table == "benchmarks_gatesetmembership":
                    join_clauses.append("left join benchmarks_gatesetmembership as o on o.gate_set_id=c.id")
                elif table == "benchmarks_gate":
                    join_clauses.append("left join benchmarks_gate as p on p.id=o.gate_id")
            elif basetable == "benchmarks_probleminstance as d":
                if table == "benchmarks_graph":
                    join_clauses.append("left join benchmarks_graph as q on q.id = d.graph_id")
                elif table == "benchmarks_problem":
                    join_clauses.append("left join benchmarks_problem as r on r.id = d.problem_id")

    sql_query = f"SELECT {', '.join(user_columns)} FROM {basetable} {' '.join(join_clauses)} "
    if filter:
        sql_query += 'where ' + ' and '.join(filter)
    print(sql_query)


    with connection.cursor() as cursor:
        try:
            cursor.execute(sql_query)
            joined_results = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
        except Exception as e:
            error_message = str(e)
            stack_trace = ""
            ErrorLog.objects.create(error_message=error_message,querycode=sql_query )
            return render(request, 'benchmarks/index.html')

    context = {
        'sql_query': sql_query,
        'joined_results': joined_results,
        'columns': columns,
        'selected_columns': user_columns,
        'selected_joins': user_joins,
        'selected_base': user_base
    }
    return render(request, 'benchmarks/custom.html', context)

def manytable(request: HttpRequest):
    user_columns = request.GET.getlist('columns')
    user_tables = request.GET.getlist('tables')
    user_filter= request.GET.getlist('filter')
    tab= user_tables[:]

    #For special metric
    extra = False
    if 'benchmarks_performancevalue' in user_tables:
        user_tables.append('benchmarks_performancemetric')
        if 'benchmarks_performancereport' in user_tables:
            extra = True
    if "benchmarks_compilationstep" in user_tables:
        user_tables.append("benchmarks_compilationtool")
        user_tables.append("benchmarks_compliationalgorithmn")
    if "benchmarks_performancereport" in user_tables:
        user_tables.append("benchmarks_solver")
    if "benchmarks_processor" in user_tables:
        user_tables.append("benchmarks_technology")


    if user_tables:
        existing_col,join_clauses = graph.connect_all(user_tables)
    else:
        join_clauses = "benchmarks_manufacturer"
        existing_col = ['benchmarks_manufacturer.name']
    #print(existing_col)
    displaycol =[]
    if not user_columns or "reset" in user_columns:
        displaycol = existing_col
    else:
        for col in user_columns:
            if col in existing_col:
                displaycol.append(col)
        if displaycol == []:
            displaycol = existing_col
    
    #For special metric
    if extra:
        displaycol.append('temp_metric.combined')
        displaycol.append('temp_metric.chosen')

    filter=[]
    if user_filter:
        for index in range(0,len(user_filter)-1,2):
            if user_filter[index+1] != '':
                filter.append("cast("+user_filter[index]+" as text )" + " like '%" + user_filter[index+1] + "%'")
    


    sql_query = f"SELECT {', '.join(displaycol)} FROM {join_clauses} "
    extrastring=''
    if extra:
        extrastringcreate = '''
        CREATE TEMPORARY TABLE temp_metric (
        performance_report_id INTEGER,
        combined TEXT,
        chosen TEXT)'''

        extrastringinsert = '''INSERT INTO temp_metric (performance_report_id, combined, chosen)
        SELECT performance_report_id,
        string_agg(value || ' ' || name, ', ') AS combined,
        MAX(CASE 
               WHEN name = 'Modularity Ratio (current/Best)' THEN value
               ELSE NULL
           END) AS chosen
        FROM benchmarks_performancevalue
        full join benchmarks_performancemetric on benchmarks_performancemetric.id = benchmarks_performancevalue.metric_id
        group by performance_report_id

        '''
        sql_query = sql_query + " full join temp_metric on benchmarks_performancereport.id = temp_metric.performance_report_id"
    if filter:
        sql_query += ' where ' + ' and '.join(filter)

    

    group=[]
    colname=[]
    groupnum={}
    
    for item in displaycol:
        groupitem = item.split('.')
        colname.append(groupitem[1])
        groupname = groupitem[0]
        groupnamelist = groupname.split('_')
        groupname1 = groupnamelist[1]
        if groupname1 not in group:
            group.append(groupname1)
            groupnum[groupname1]=1
        else:
            groupnum[groupname1]+=1
    
    #print(group)
    #print(groupnum)
    combined = [(name, groupnum[name]) for name in group]
    print(sql_query)
    with connection.cursor() as cursor:
            if extra:
                cursor.execute(extrastringcreate)
                cursor.execute(extrastringinsert)
            cursor.execute(sql_query)
            joined_results = cursor.fetchall()
            columns = displaycol

    context = {
        'sql_query': sql_query,
        'joined_results': joined_results,
        'columns': columns,
        'selected_columns': user_columns,
        'selected_tables': tab,
        'colname': colname,
        'combined': combined,
    }
    return render(request, 'benchmarks/ManyTableBackup.html', context)

@staff_member_required
def dataupload(request): # handles csv uploads
    performance_report_form = PerformanceReportForm()
    problem_form = ProblemForm()

    context = {
        'performance_report_form': performance_report_form,
        'performance_report_upload_summary': '',
        'problem_form': problem_form,
        'problem_upload_summary': '',
        'has_permission': True
    }

    if request.method == 'POST':
        if 'performanceReportFile' in request.FILES:
            performance_report_form = PerformanceReportForm(request.POST, request.FILES)

            if performance_report_form.is_valid():
                temporaryFile = "tmp" + request.FILES["performanceReportFile"].name
                with open(temporaryFile, "wb+") as file:
                    for chunk in request.FILES["performanceReportFile"].chunks():
                        file.write(chunk)

                upload_summary = handle_performance_report_upload(temporaryFile)
                context['performance_report_upload_summary'] = upload_summary

                os.remove(temporaryFile)

        elif 'problemFile' in request.FILES:
            problem_form = ProblemForm(request.POST, request.FILES)

            if problem_form.is_valid():
                temporaryFile = "tmp" + request.FILES["problemFile"].name
                with open(temporaryFile, "wb+") as file:
                    for chunk in request.FILES["problemFile"].chunks():
                        file.write(chunk)

                upload_summary = handle_problem_upload(temporaryFile)
                context['problem_upload_summary'] = upload_summary

                os.remove(temporaryFile)

    return render(request, 'admin/csvupload.html', context=context)
