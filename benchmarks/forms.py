from django import forms

class PerformanceReportForm(forms.Form):
    performanceReportFile = forms.FileField(allow_empty_file=False, label='')

class ProblemForm(forms.Form):
    problemFile = forms.FileField(allow_empty_file=False, label='')

class ProcessorForm(forms.Form):
    processorFile = forms.FileField(allow_empty_file=False, label='')