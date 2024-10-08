from django.db import models
from django.core.exceptions import ValidationError

# Single Column Models
class Manufacturer(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        return self.name

class Technology(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        return self.name
    
class Solver(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        return self.name

class PerformanceMetric(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        return self.name

class CompilationTool(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        return self.name

class CompilationAlgorithmn(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        return self.name

# Multi-Column Models 
class Topology(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    physical_qubits_per_cell = models.IntegerField(null=True, blank=True)
    qubit_degree = models.FloatField(null=True, blank=True)
    qubit_nominal_length = models.IntegerField(null=True, blank=True, default=None)
    max_qubo_variable_count_clique = models.IntegerField(null=True, blank=True, default=None)
    url1 = models.URLField(max_length=200, null= True, blank=True)
    url2 = models.URLField(max_length=200, null = True, blank=True)
    notes = models.TextField(null=True, blank=True,)

    def __str__(self):
        return self.name

class Processor(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    technology = models.ForeignKey(Technology, on_delete=models.SET_NULL, null=True, blank=False)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.SET_NULL, null=True, blank=False)
    physical_qubits = models.IntegerField(null=True, blank=True, default=None)
    topology = models.ForeignKey(Topology, on_delete=models.SET_NULL, null=True, blank=False)
    intro_year = models.IntegerField(null=True, blank=True, default=None)
    rep_rate = models.FloatField(null=True, blank=True, default=None)
    url1 = models.URLField(max_length=200, null=True, blank=True,)
    url2 = models.URLField(max_length=200, null=True, blank=True,)
    notes = models.TextField(null=True, blank=True,)

    def __str__(self):
        return self.name
    
class GateSet(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    url1 = models.URLField(max_length=200, null=True, blank=True)
    url2 = models.URLField(max_length=200, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
    
class Gate(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    qubits = models.IntegerField(null=False, blank=False)
    url1 = models.URLField(max_length=200, blank=True)
    url2 = models.URLField(max_length=200, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.qubits}, {self.name}"
    
class GateSetMembership(models.Model):
    gate_set = models.ForeignKey(GateSet, on_delete=models.SET_NULL, null=True, blank=False)
    gate = models.ForeignKey(Gate, on_delete=models.SET_NULL, null=True, blank=False)

    def __str__(self):
        return f"{self.gate_set} - {self.gate.qubits}Q {self.gate.name}"

class System(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    manufactor = models.ForeignKey(Manufacturer,  on_delete=models.SET_NULL, null=True, blank=True)
    processor = models.ForeignKey(Processor, on_delete=models.SET_NULL, null=True, blank=True)
    intro_year = models.IntegerField(null=True, blank=True, default=None)
    gate_set = models.ForeignKey(GateSet, on_delete=models.SET_NULL, null=True, blank=True)
    url1 = models.URLField(max_length=200, null=True, blank=True)
    url2 = models.URLField(max_length=200, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class Calibration(models.Model):
    system = models.ForeignKey(System, on_delete=models.SET_NULL, null=True, blank=False)
    date = models.DateTimeField(null=True, blank=True, default=None)
    eplg = models.FloatField(null=True, blank=True, default=None)
    clops = models.IntegerField(null=True, blank=True, default=None)
    median_cz_err = models.FloatField(null=True, blank=True, default=None)
    median_ecr_err = models.FloatField(null=True, blank=True, default=None)
    median_cnot_err = models.FloatField(null=True, blank=True, default=None)
    median_sx_err = models.FloatField(null=True, blank=True, default=None)
    min_1q_err = models.FloatField(null=True, blank=True, default=None)
    max_1q_err = models.FloatField(null=True, blank=True, default=None)
    typical_1q_err = models.FloatField(null=True, blank=True, default=None)
    median_1q_err = models.FloatField(null=True, blank=True, default=None)
    min_2q_err = models.FloatField(null=True, blank=True, default=None)
    max_2q_err = models.FloatField(null=True, blank=True, default=None)
    typical_2q_err = models.FloatField(null=True, blank=True, default=None)
    median_2q_err = models.FloatField(null=True, blank=True, default=None)
    median_readout_err = models.FloatField(null=True, blank=True, default=None)
    spam_err = models.FloatField(null=True, blank=True, default=None)
    mem_err_avg_d1_circuit = models.FloatField(null=True, blank=True, default=None)
    crosstalk_err_mid_circuit = models.FloatField(null=True, blank=True, default=None)
    min_t1 = models.FloatField(null=True, blank=True, default=None)
    max_t1 = models.FloatField(null=True, blank=True, default=None)
    median_t1 = models.FloatField(null=True, blank=True, default=None)
    mean_t1 = models.FloatField(null=True, blank=True, default=None)
    min_t2 = models.FloatField(null=True, blank=True, default=None)
    max_t2 = models.FloatField(null=True, blank=True, default=None)
    median_t2 = models.FloatField(null=True, blank=True, default=None)
    mean_t2 = models.FloatField(null=True, blank=True, default=None)
    url1 = models.URLField(max_length=200, null=True, blank=True)
    url2 = models.URLField(max_length=200, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
class Graph(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    url1 = models.URLField(max_length=200, null= True,  blank=True)
    url2 = models.URLField(max_length=200,null = True,  blank=True)
    notes = models.TextField(null = True, blank=True)

    def __str__(self):
        return self.name
    
class Problem(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    url1 = models.URLField(max_length=200, null = True,  blank=True)
    url2 = models.URLField(max_length=200, null = True, blank=True)
    notes = models.TextField(null=True, blank=True)
    def __str__(self):
        return f"{self.name}, {self.notes}"

class ProblemInstance(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.SET_NULL, null=True, blank=False)
    graph = models.ForeignKey(Graph, on_delete=models.SET_NULL, null = True, blank= False)
    graph_size= models.FloatField(null=True, blank=False, default=None)
    url1 = models.URLField(max_length=200, null = True, blank=True)
    url2 = models.URLField(max_length=200, null = True, blank=True)
    notes = models.TextField(null=True, blank=True, default=None)

class PerformanceReport(models.Model):
    problem = models.ForeignKey(ProblemInstance, on_delete=models.SET_NULL, null=True, blank=True)
    qubo_var_count = models.IntegerField(null=True, blank=True, default=None)
    qubo_quad_term_count = models.IntegerField(null=True, blank=True, default=None)
    system = models.ForeignKey(System, on_delete=models.CASCADE, null=True, blank=True, default=None)
    solver = models.ForeignKey(Solver, on_delete=models.CASCADE, null=True, blank=True, default=None)
    qubit_count = models.IntegerField(null=True, blank=True, default=None)
    rcs = models.FloatField(null=True, blank=True, default=None)
    mean_chain_length = models.IntegerField(null=True, blank=True, default=None)
    max_chain_length = models.IntegerField(null=True, blank=True, default=None)
    num_runs = models.IntegerField(null=True, blank=True, default=None)
    url1 = models.URLField( null=True, blank=True)
    url2 = models.URLField( null=True, blank=True)
    notes = models.TextField(null=True, blank=True, default=None)

    

    
# New Multiple Columns Model
class CompilationStep(models.Model):
    compilation_tool = models.ForeignKey(CompilationTool,on_delete=models.SET_NULL, null=True, blank=True)
    version = models.FloatField(null=True, blank=True, default=None)
    compilation_algorithmn = models.ForeignKey(CompilationAlgorithmn, on_delete=models.SET_NULL, null=True, blank=False)
    performance_report = models.ForeignKey(PerformanceReport, on_delete=models.SET_NULL, null=True, blank=False)

    def __str__(self):
        return f"{self.compilation_tool}, {self.compilation_algorithmn}"
class PerformanceValue(models.Model):
    metric = models.ForeignKey(PerformanceMetric, on_delete=models.SET_NULL, null=True, blank=False)
    value = models.FloatField(null=True, blank=False, default=None)
    performance_report = models.ForeignKey(PerformanceReport,on_delete=models.SET_NULL, null=True, blank=False)

    def __str__(self):
        return f"{self.metric}, {self.value}, {self.performance_report_id}"

class ErrorLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    error_message = models.TextField()
    
    querycode= models.TextField()
