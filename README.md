# QuantumBenchmarkingDB
## Setup Steps
1. Install project requirements (use of a virtual environment is reccomended)
    ```bash
    pip install -r requirements.txt
    ```
2. Create tables associated with benchmarking app
    ```bash
    python3 manage.py makemigrations benchmarks
    python3 manage.py migrate
    ```
    - If desired to use an existing .sqlite3 file, place .sqlite3 file within home directory
3. Create a superuser for Django App
    ```bash
    python3 manage.py createsuperuser
    ```
    - Will prompt for Username, Email, and Password
5. Launch Django Server
    ```bash
    python3 manage.py runserver
    ```

## Notable Functionalities
### Depth First Search Algorithm
#### Implementation
- The algorithm can be found in `benchmarks/graph.py`.
- Focus on the `connect_all()` function which implements DFS.
- The function records the path while finding the vertex. If it finds the vertex, it adds it to the output.

#### Avoiding Duplicates
   - Ensure no duplicate nodes in the path to avoid SQL issues. If a node detects a vertex in its lower hierarchy, it will not record itself.

#### Adding New Tables and Connections
   - Add new tables:
     ```python
     graph.add_vertex('benchmarks_manufacturer')
     ```
   - Add new connections:
     ```python
     graph.add_edge('benchmarks_manufacturer', 'benchmarks_system', 'benchmarks_manufacturer.id = benchmarks_system.manufactor_id')
     graph.add_edge('benchmarks_manufacturer', 'benchmarks_processor', 'benchmarks_manufacturer.id = benchmarks_processor.manufacturer_id')
     ```
   - Add columns for display:
     ```python
     graph.add_col('benchmarks_manufacturer', ['benchmarks_manufacturer.name'])
     ```

### CSV File Upload in Admin Site
#### Implementation
- Functionality for handling performance report and problem uploads can be found in `benchmarks/csvupload.py`.
- Functions for each upload are largely based on Django commands for csv uploads found in `benchmarks/management/commands/`.
- To enable editing of Django's Admin site, a custom admin site (`AdminSiteBench`) was created in `benchmarks/admin.py`. This allowed for the creation of an additional admin page and for the overriding of the admin sites index page
- HTML files for the custom admin site can be found in `benchmarks/templates/admin/`
#### Further Development
- There exists a Django command for uploading csv files with processor data so it is natural for this to be the next addition to the admin site.

# Django Guide for Future Developers
## Django Admin Site
Django automatically provides a way to manipulate table data through its admin interface. "It reads metadata from your models to provide a quick, model-centric interface where trusted users can manage content on your site" ([DjangoProject](https://docs.djangoproject.com/en/5.0/ref/contrib/admin/)). 

To make newly created models accessible within the admin interface, they must be registered to the admin site using the `admin.py` file within their project directory (see [this guide](https://medium.com/django-unleashed/django-project-structure-a-comprehensive-guide-4b2ddbf2b6b8) for information on how Django projects are structured)

### Accessing Admin Site
To log into the site, open the `/admin` URL and enter the credentials for a superuser. Once inside, you can manipulate the metadata associated with the models that are registered to be admin accessible.

## Creating New Pages
- Create a new HTML file in `benchmarks/templates/benchmarks` for pages on the main site. For pages on the admin site, create files in `benchmarks/templates/admin`
- It's best practice to use header templates in order to have a consistent and functioning header between pages. Refer to exisiting pages for guidance on this front.

## Making Links to a Page
### Views
- Start with `views.py` in the `benchmarks` directory.
- Create a function specifically for the HTML page.
- This is where most backend processing occurs. For static pages, create a function like the example provided. For dynamic pages, you can write code, process data, and send it to the page (more on this later).

### URLs
- Open `urls.py`.
- Add the path for your new page and link it to the function created in `views.py`:

```python
path('your-new-page-url/', views.your_new_function),
```

Views and Urls are crucial to understand when developing with Django. If its your first time working with Django, head to [Django's official site](https://www.djangoproject.com/start/) to learn more

## Loading Static Files
- Put this block at the top of your page:
  ```django
  {% load static %}
  ```
- To link to any static file, use the format:
  ```django
  "{% static 'benchmarks/path_to_file' %}"
  ```
  Example:
  ```django
  "{% static 'benchmarks/css/style4.css' %}"
  ```
- The static folder can be found at `benchmarks/static`.

## Custom Django Console Commands
### Creating Commands for Data Importing
- Create a `.py` file under `benchmarks/management/commands`.
- Use the following template:
  ```python
  import pandas as pd
  from django.core.management.base import BaseCommand
  from django.db import connection
  class Command(BaseCommand):
      help = 'Load data from CSV file and join with existing tables'
      def add_arguments(self, parser):
          parser.add_argument('csv_file', type=str, help='Path to the CSV file')
      def handle(self, *args, **kwargs):
          csv_file = kwargs['csv_file']
          # Read the CSV file into a DataFrame
          df = pd.read_csv(csv_file)
          # Connect to the SQLite database
          with connection.cursor() as cursor:
              # Your database interaction code here
  ```

### Explanation
- Create a temporary table for easier manipulation of incoming data.
- Insert data line by line into the temporary table.
- Process the temporary table and insert data into the main table, handling errors as needed.

### Execute the Command
- Navigate to the main project directory.
- Run:
  ```shell
  python manage.py load_data <path_to_csv_file>
  ```
- It's recommended to place the CSV file in the same directory as `manage.py` for easier access.

## SQL in Django
### Executing Commands
- Write the SQL command string.
- Use `cursor.execute(str)` to execute the command.
- Execute one command at a time.
  ```python
  create_temp_table_sql = """
  CREATE TEMPORARY TABLE temp_table (
      Manufacturer TEXT,
      qubo INTEGER,
      system_name TEXT,
      embedding_algorithm TEXT,
      solver TEXT,
      url TEXT,
      qubits INTEGER,
      rcs FLOAT,
      number_of_runs INTEGER,
      time_type TEXT,
      time FLOAT,
      performance_metric TEXT,
      performance_value FLOAT,
      notes TEXT
  )
  """
  cursor.execute(create_temp_table_sql)
  ```

### SQL Statements with Variable Values
- Use placeholders:
  ```python
  insert_sql = '''
  INSERT INTO temp_table (id, problemid, qubo, system_name, embedding_algorithm, solver, url, qubits, rcs, number_of_runs, time_type, time, performance_metric, performance_value, notes)
  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
  '''
  cursor.execute(insert_sql, arr_of_values)
  ```

## Creating and Editing Database Models
### Creating Models
- Define new classes in `models.py`.

### Editing Models
- Modify existing classes as needed. Django will adapt to your changes.

### Applying Changes
- Run the following commands:
  ```shell
  python manage.py makemigrations
  python manage.py migrate
  ```

## Common Errors to Watch For
- Misspellings like ‘manufactor’ vs ‘manufacturer’.
- Database names follow this format: `benchmarks_tablename`.
- Foreign keys follow this format: `name_id`.
- Avoid appending `_id` to foreign key names; it's automatically included.
- Use lowercase for all naming conventions; Linux is case-sensitive.

## Deployment
Refer to this guide: [Django on Red Hat](https://www.checkmateq.com/blog/django-red-hat)

## Additional Reading
For those working with Django for the first time, check out [Django's official site](https://www.djangoproject.com/start/)
