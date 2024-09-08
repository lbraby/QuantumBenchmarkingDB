import pandas as pd
import csv, json
from django.db import connection
from csvvalidator import CSVValidator, HEADER_CHECK_FAILED, RECORD_LENGTH_CHECK_FAILED, VALUE_CHECK_FAILED

def type_check(value, type_class, nulls_allowed=False):
    """
    Perform a type check on passed value. Raise error on type mismatch and null values (if not alowed)

    Arguments
        ---------

        `value` - value to perform type check on

        `type_class` - type to check against

        `nulls_allowed` - If set to False, raises ValueError on '' and None
    """
    if value is None or value == '' and nulls_allowed == False:
        raise ValueError
    elif value is None or value == '' and nulls_allowed == True:
        return
    
    type_class(value)

def schema_toString(schema):
    for col in schema:
        schema[col] = f"{schema[col][0].__name__}{' (nullable)' if None in schema[col] else ''}"
    
    return json.dumps(schema, indent=4)

def validate_csv(file_path, schema):
    """
    Perform schema validation on provided csv file. Return a list of errors where each error is a dict in the form {"text": [str], "message_type": "error"}

    Arguments
        ---------

        `file_path` - path of csv file to be validated

        `schema` - dictionary where keys are column names and values are lists of acceptable types (add None to value list for nullable columns)
    """
    # check that required columns are present and remove unrequired columns from schema when not found in file header
    missing_columns = []
    with open(file_path) as csvfile:
        reader = csv.reader(csvfile)
        column_names = next(reader)
    for column in list(schema.keys()):
        if column not in column_names:
            if None not in schema[column]:
                missing_columns.append(column)
            else:
                del schema[column]
    if missing_columns:
        return [{"text": f"Header Error: missing required headers ({', '.join(missing_columns)})", "message_type": "error"}]

    validator = CSVValidator(schema.keys())
    validator.add_header_check() #check that header matches refined schema
    validator.add_record_length_check() # check that len(row) = len(header)

    for column, types in schema.items(): # perform type checks against schema
        if None not in types:
            validator.add_value_check(column, 
                                      lambda v, t=types[0]: type_check(v, t, False), 
                                      message=f"{column} column expects nonnull {types[0].__name__}s")
        else:
            validator.add_value_check(column, 
                                      lambda v, t=types[0]: type_check(v, t, True),
                                      message=f"{column} column expects nullable {types[0].__name__}s")

    with open(file_path) as csvfile:
        data = csv.reader(csvfile)
        problems = validator.validate(data)

    error_messages = []
    for problem in problems:
        if problem["code"] == HEADER_CHECK_FAILED:
            error_messages.append({"text": f"Header Error: bad header", "message_type": "error"})
        elif problem["code"] == RECORD_LENGTH_CHECK_FAILED:
            error_messages.append({"text": f"Record Length Error (row {problem['row'] - 1}): length {problem['length']}", "message_type": "error"})
        elif problem["code"] == VALUE_CHECK_FAILED:
            error_messages.append({"text": f"Value Error (row {problem['row'] - 1}): {problem['message']}", "message_type": "error"})

    return error_messages

def handle_performance_report_upload(file_path):
    upload_summary = {"status": "success", "top_message": "", "messages": []}
    file_schema = {"Problem ID": [int], "QUBO Variables": [int, None], "QUBO Quadratic Terms": [int, None], "System Name": [str, None], "Embedding Algorithm": [str, None], 
                   "Solver": [str, None], "URL": [str, None], "Qubits": [int, None], "RCS": [float, None], "Mean Chain Length": [int, None], "Max Chain Length": [int, None],
                   "Number of Runs": [int, None], "Time Type": [str, None], "Time": [float, None], "Performance Metric": [str, None], "Performance Value": [float, None],
                   "Notes": [str, None]}

    # return with error messages if csv file does not follow set schema
    error_messages = validate_csv(file_path, file_schema.copy())
    if error_messages:
        upload_summary["status"] = "error"
        upload_summary["top_message"] = f"Uploaded file failed schema validation"
        upload_summary["schema"] = "Schema: " + schema_toString(file_schema)
        upload_summary["messages"] = error_messages

        return upload_summary

    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Connect to the SQLite database
    with connection.cursor() as cursor:
        # Create a temporary table
        create_temp_table_sql = """
        CREATE TEMPORARY TABLE temp_table (
            problemid INTEGER,
            qubo INTEGER,
            qubo_quadratic INTEGER,
            system_name TEXT,
            embedding_algorithm TEXT,
            solver TEXT,
            url TEXT,
            qubits INTEGER,
            rcs FLOAT,
            mean_chain_length INTEGER,
            max_chain_length INTEGER,
            number_of_runs INTEGER,
            time_type TEXT,
            time FLOAT,
            performance_metric TEXT,
            performance_value FLOAT,
            notes TEXT,
            rownum int
        )
        """
        cursor.execute(create_temp_table_sql)

        # Insert data from the DataFrame into the temporary table
        insert_sql = '''
        INSERT INTO temp_table (problemid, qubo, qubo_quadratic, system_name, embedding_algorithm, solver, url, qubits, rcs, mean_chain_length, max_chain_length, number_of_runs, time_type, time, performance_metric, performance_value, notes, rownum)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        for index, row in df.iterrows():
            try:
                problemid = None if pd.isna(row['Problem ID']) else int(row['Problem ID'])
                qubo = None if pd.isna(row['QUBO Variables']) else int(row['QUBO Variables'])
                qubo_quadratic = None if pd.isna(row['QUBO Quadratic Terms']) else int(row['QUBO Quadratic Terms'])
                system_name = None if pd.isna(row['System Name']) else (row['System Name'])
                embedding_algorithm = None if pd.isna(row['Embedding Algorithm']) else (row['Embedding Algorithm'])
                solver = None if pd.isna(row['Solver']) else (row['Solver'])
                url = None if pd.isna(row['URL']) else (row['URL'])
                qubits = None if pd.isna(row['Qubits']) else int(row['Qubits'])
                rcs = None if pd.isna(row['RCS']) else float(row['RCS'])
                mean_chain_length = None if pd.isna(row['Mean Chain Length']) else int(row['Mean Chain Length'])
                max_chain_length = None if pd.isna(row['Max Chain Length']) else int(row['Max Chain Length'])
                number_of_runs = None if pd.isna(row['Number of Runs']) else int(row['Number of Runs'])
                time_type = None if pd.isna(row['Time Type']) else (row['Time Type'])
                time = None if pd.isna(row['Time']) else float(row['Time'])
                performance_metric = None if pd.isna(row['Performance Metric']) else (row['Performance Metric'])
                performance_value = None if pd.isna(row['Performance Value']) else float(row['Performance Value'])
                notes = None if pd.isna(row['Notes']) else (row['Notes'])
                rownum = index + 1
                # Prepare the values tuple
                values = (
                    problemid, qubo, qubo_quadratic, system_name, embedding_algorithm, solver, url, qubits, rcs, mean_chain_length, max_chain_length, number_of_runs, time_type, time, performance_metric, performance_value, notes, rownum
                )

                # Execute the SQL statement
                cursor.execute(insert_sql, values)
            except Exception as e:
                upload_summary["messages"].append({"text": f"Temporary Table Insertion Error (row {rownum}): {e}", "message_type": "error"})
        
        cursor.execute("SELECT * FROM temp_table")
        rows = cursor.fetchall()

        check_system_sql = 'SELECT id FROM benchmarks_system WHERE name = %s'
        insert_system_sql = 'INSERT INTO benchmarks_system(name) values (%s)'

        check_algorithm_sql = 'SELECT id FROM benchmarks_CompilationAlgorithmn WHERE name = %s'
        insert_algorithm_sql = 'INSERT INTO benchmarks_CompilationAlgorithmn(name) values (%s)'

        check_solver_sql = 'SELECT id FROM benchmarks_solver WHERE name = %s'
        insert_solver_sql = 'INSERT INTO benchmarks_solver(name) values (%s)'

        check_metric_sql = 'SELECT id FROM benchmarks_PerformanceMetric WHERE name = %s'
        insert_metric_sql = 'INSERT INTO benchmarks_PerformanceMetric(name) values (%s)'

        check_report_sql = '''
            Select id 
            FROM benchmarks_performancereport
            where problem_id = %s
            and (qubo_var_count = %s OR (%s is NULL and qubo_var_count is NULL))
            and (qubo_quad_term_count = %s OR (%s is NULL and qubo_quad_term_count is NULL))
            and (system_id = %s OR (%s is NULL and system_id is NULL))
            and (solver_id = %s OR (%s is NULL and solver_id is NULL))
            and (qubit_count = %s OR (%s is NULL and qubit_count is NULL))
            and (rcs = %s OR (%s is NULL and rcs is NULL))
            and (mean_chain_length = %s OR (%s is NULL and mean_chain_length is NULL))
            and (max_chain_length = %s OR (%s is NULL and max_chain_length is NULL))
            and (num_runs = %s OR (%s is NULL and num_runs is NULL))
            '''
        insert_report_sql = '''INSERT INTO benchmarks_performancereport
        (problem_id,
        qubo_var_count,
        qubo_quad_term_count,
        system_id,
        solver_id,
        qubit_count,
        rcs,
        mean_chain_length,
        max_chain_length,
        num_runs,
        url1,
        notes)
        values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        '''

        check_value_sql = '''
            Select id 
            FROM benchmarks_PerformanceValue
            where metric_id = %s and value = %s and performance_report_id = %s
            '''
        insert_value_sql = '''INSERT INTO benchmarks_PerformanceValue
        (metric_id,
        value,
        performance_report_id)
        values(%s,%s,%s)
        '''

        check_compilation_sql = '''
        Select id
        FROM benchmarks_CompilationStep
        where compilation_algorithmn_id = %s and performance_report_id = %s
        '''
        insert_compilation_sql = '''INSERT INTO benchmarks_CompilationStep
        (compilation_algorithmn_id,
        performance_report_id)
        values(%s,%s)
        '''

        insertions = {"performance_reports": 0, "performance_values": 0, "time_values": 0, "compilation_steps": 0,"systems": 0, "embedding_algorithms": 0, "solvers": 0, "metrics": 0}
        for row in rows:
            # Here, you can process each row and use the variables as needed
            problemid = row[0]
            qubo = row[1]
            qubo_quadratic = row[2]
            system_name = row[3]
            embedding_algorithm = row[4]
            solver = row[5]
            url = row[6]
            qubits = row[7]
            rcs = row[8]
            mean_chain_length = row[9]
            max_chain_length = row[10]
            number_of_runs = row[11]
            time_type = row[12]
            time = row[13]
            performance_metric = row[14]
            performance_value = row[15]
            notes = row[16]
            rownum = row[17]

            # TODO: row_summary = {'Problem ID': problemid, 'QUBO Variables': qubo, 'QUBO Quadratic Terms': qubo_quadratic, 'System Name': system_name, 'Embedding Algorithm': embedding_algorithm, 'Solver': solver, 'URL': url, 'Qubits': qubits, 'RCS': rcs, 'Mean Chain Length': mean_chain_length, 'Max Chain Length': max_chain_length, 'Number of Runs': number_of_runs, 'Time Type': time_type, 'Time': time, 'Performance Metric': performance_metric, 'Performance Value': performance_value, 'Notes': notes}

            system_id = None
            embedding_algorithm_id = None
            solver_id = None
            time_id = None
            metric_id = None


            # System Foreign Key
            if system_name is not None:
                cursor.execute(check_system_sql, [system_name])
                check = cursor.fetchall()

                if len(check) == 0:
                    cursor.execute(insert_system_sql, [system_name])
                    upload_summary["messages"].append({"text": f"New System (row {rownum}): {system_name}", "message_type": "success"})
                    connection.commit()
                    insertions["systems"] += 1

                cursor.execute(check_system_sql, [system_name])
                system_get_id = cursor.fetchall()
                if system_get_id: # foreign key correctly found
                    system_id = system_get_id[0][0]
                else: # cannot insert entry due to foreign key error
                    upload_summary["messages"].append({"text": f"Insertion Error (row {rownum}): System {system_name} was not found after insertion.", "message_type": "error"})
                    continue


            # Embedding Algorithm Foreign Key
            if embedding_algorithm is not None:
                cursor.execute(check_algorithm_sql, [embedding_algorithm])
                check = cursor.fetchall()

                if len(check) == 0:
                    cursor.execute(insert_algorithm_sql, [embedding_algorithm])
                    upload_summary["messages"].append({"text": f"New Embedding Algorithm (row {rownum}): {embedding_algorithm}", "message_type": "success"})
                    connection.commit()
                    insertions["embedding_algorithms"] += 1

                cursor.execute(check_algorithm_sql, [embedding_algorithm])
                algorithm_get_id = cursor.fetchall()
                if algorithm_get_id: # foreign key correctly found
                    embedding_algorithm_id = algorithm_get_id[0][0]
                else: # cannot insert entry due to foreign key error
                    upload_summary["messages"].append({"text": f"Insertion Error (row {rownum}): Embedding Algorithm {embedding_algorithm} was not found after insertion.", "message_type": "error"})
                    continue


            # Solver Foreign Key
            if solver is not None:
                cursor.execute(check_solver_sql, [solver])
                check = cursor.fetchall()

                if len(check) == 0:
                    cursor.execute(insert_solver_sql, [solver])
                    upload_summary["messages"].append({"text": f"New Solver (row {rownum}): {solver}", "message_type": "success"})
                    connection.commit()
                    insertions["solvers"] += 1

                cursor.execute(check_solver_sql, [solver])
                solver_get_id = cursor.fetchall()
                if solver_get_id: # foreign key correctly found
                    solver_id = solver_get_id[0][0]
                else: # cannot insert entry due to foreign key error
                    upload_summary["messages"].append({"text": f"Insertion Error (row {rownum}): Solver {solver} was not found after insertion.", "message_type": "error"})
                    continue


            # Time Type (Performance Metric) Foreign Key
            if time_type is not None:
                cursor.execute(check_metric_sql, [time_type])
                check = cursor.fetchall()

                if len(check) == 0:
                    cursor.execute(insert_metric_sql, [time_type])
                    upload_summary["messages"].append({"text": f"New Time Type (Performance Metric) (row {rownum}): {time_type}", "message_type": "success"})
                    connection.commit()
                    insertions["metrics"] += 1

                cursor.execute(check_metric_sql, [time_type])
                time_type_get_id = cursor.fetchall()
                if time_type_get_id: # foreign key correctly found
                    time_id = time_type_get_id[0][0]
                else: # cannot insert entry due to foreign key error
                    upload_summary["messages"].append({"text": f"Insertion Error (row {rownum}): Time Type (Performance Metric) {time_type} was not found after insertion.", "message_type": "error"})
                    continue


            # Performance Metric Foreign Key
            if performance_metric is not None:
                cursor.execute(check_metric_sql, [performance_metric])
                check = cursor.fetchall()

                if len(check) == 0:
                    cursor.execute(insert_metric_sql, [performance_metric])
                    upload_summary["messages"].append({"text": f"New Performance Metric (row {rownum}): {performance_metric}", "message_type": "success"})
                    connection.commit()
                    insertions["metrics"] += 1

                cursor.execute(check_metric_sql, [performance_metric])
                performance_metric_get_id = cursor.fetchall()
                if performance_metric_get_id: # foreign key correctly found
                    metric_id = performance_metric_get_id[0][0]
                else: # cannot insert entry due to foreign key error
                    upload_summary["messages"].append({"text": f"Insertion Error (row {rownum}): Performance Metric {performance_metric} was not found after insertion.", "message_type": "error"})
                    continue


            # Performance Report
            cursor.execute(check_report_sql, (problemid, qubo, qubo, qubo_quadratic, qubo_quadratic, system_id, system_id, solver_id, solver_id, qubits, qubits, rcs, rcs, mean_chain_length, mean_chain_length, max_chain_length, max_chain_length, number_of_runs, number_of_runs))
            report_check = cursor.fetchall()

            insert_compilation = False
            insert_time_value = False
            insert_metric_value = False
            if len(report_check) > 0: # report already exists
                upload_summary["messages"].append({"text": f"Exception (row {rownum}): Entry already exists in Performance Report table", "message_type": "exception"})
                report_id = report_check[0][0]
                if embedding_algorithm_id: # check if report and embedding algorithm already in Compilation Step
                    cursor.execute(check_compilation_sql, (embedding_algorithm_id, report_id))
                    check = cursor.fetchall()
                    if len(check) > 0: 
                        upload_summary["messages"].append({"text": f"Exception (row {rownum}): report, embedding algorithm already in Compilation Step table", "message_type": "exception"})
                    else: insert_compilation = True

                if time_id: # check if report and time performance already in Performance Value
                    cursor.execute(check_value_sql, (time_id, time, report_id))
                    check = cursor.fetchall()
                    if len(check) > 0:
                        upload_summary["messages"].append({"text": f"Exception (row {rownum}): report, time already in Performance Value table", "message_type": "exception"})
                    else: insert_time_value = True

                if metric_id: # check if report and performance value already in Performance Value
                    cursor.execute(check_value_sql, (metric_id, performance_value, report_id))
                    check = cursor.fetchall()
                    if len(check) > 0:
                        upload_summary["messages"].append({"text": f"Exception (row {rownum}): report, performance in Performance Value table", "message_type": "exception"})
                    else: insert_metric_value = True

            else: # insert new report
                cursor.execute(insert_report_sql, (problemid, qubo, qubo_quadratic, system_id, solver_id, qubits, rcs, mean_chain_length, max_chain_length, number_of_runs, url, notes))
                # TODO: upload_summary["messages"].append({"text": f"New Performance Report: {row_summary}", "message_type": "success"})
                connection.commit()
                insertions["performance_reports"] += 1

                insert_compilation = True
                insert_time_value = True
                insert_metric_value = True

            # get report id to reference for insertions into Compilation Step and Performance Value
            cursor.execute(check_report_sql, (problemid, qubo, qubo, qubo_quadratic, qubo_quadratic, system_id, system_id, solver_id, solver_id, qubits, qubits, rcs, rcs, mean_chain_length, mean_chain_length, max_chain_length, max_chain_length, number_of_runs, number_of_runs))
            report_get_id = cursor.fetchall()

            if report_get_id: 
                report_id = report_get_id[0][0]

                if embedding_algorithm_id and insert_compilation:
                    print((embedding_algorithm_id, report_id))
                    cursor.execute(insert_compilation_sql, (embedding_algorithm_id, report_id))
                    connection.commit()
                    insertions["compilation_steps"] += 1

                if time_id and insert_time_value:
                    print((time_id, time, report_id))
                    cursor.execute(insert_value_sql, (time_id, time, report_id))
                    connection.commit()
                    insertions["time_values"] += 1

                if metric_id and insert_metric_value:
                    print((metric_id, performance_value, report_id))
                    cursor.execute(insert_value_sql, (metric_id, performance_value, report_id))
                    connection.commit()
                    insertions["performance_values"] += 1
            else:
                upload_summary["messages"].append({"text": f"Insertion Error (row {rownum}): Performance Report could not be found after insertion", "message_type": "error"})
            
    upload_summary["top_message"] = f"Upload Summary: {df.shape[0]} rows read, {insertions['performance_reports']} performance reports inserted"
    if insertions["performance_values"]:
        upload_summary["top_message"] += f", {insertions['performance_values']} performance values inserted"
    if insertions["time_values"]:
        upload_summary["top_message"] += f", {insertions['time_values']} time values inserted"
    if insertions["compilation_steps"]:
        upload_summary["top_message"] += f", {insertions['compilation_steps']} compilation steps inserted"
    if insertions["systems"]:
        upload_summary["top_message"] += f", {insertions['systems']} new systems"
    if insertions["embedding_algorithms"]:
        upload_summary["top_message"] += f", {insertions['embedding_algorithms']} new compilation (embedding) algorithms"
    if insertions["solvers"]:
        upload_summary["top_message"] += f", {insertions['solvers']} new solvers"
    if insertions["metrics"]:
        upload_summary["top_message"] += f", {insertions['metrics']} new performance metrics"
    return upload_summary

def handle_problem_upload(file_path):
    upload_summary = {"status": "success", "top_message": "", "messages": []}
    file_schema = {"Problem": [str], "Graph Size": [float, None], "Graph Type": [str], "url": [str, None], "Notes": [str, None]}

    # return with error messages if csv file does not follow set schema
    error_messages = validate_csv(file_path, file_schema.copy())
    if error_messages:
        upload_summary["status"] = "error"
        upload_summary["top_message"] = f"Uploaded file failed schema validation"
        upload_summary["schema"] = "Schema: " + schema_toString(file_schema)
        upload_summary["messages"] = error_messages

        return upload_summary

    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Connect to the SQLite database
    with connection.cursor() as cursor:
        # Create a temporary table
        create_temp_table_sql = """
        CREATE TEMPORARY TABLE temp_table (
            problem text,
            graphsize float,
            graphtype text,
            url text,
            note text,
            rownum int
        )
        """
        cursor.execute(create_temp_table_sql)

        # Insert data from the DataFrame into the temporary table
        insert_sql = '''
        INSERT INTO temp_table (problem, graphsize, graphtype, url, note, rownum)
        VALUES (%s, %s, %s, %s, %s, %s)
        '''
        for index, row in df.iterrows():
            try:
                problem = None if pd.isna(row['Problem']) else row['Problem']
                graphsize = None if pd.isna(row['Graph Size']) else float(row['Graph Size'])
                graphtype = None if pd.isna(row['Graph Type']) else row['Graph Type']
                url = None if pd.isna(row['url']) else row['url']
                note = None if pd.isna(row['Notes']) else row['Notes']
                rownum = index + 1
                # Prepare the values tuple
                values = (
                    problem, graphsize, graphtype, url, note, rownum)
                
                # Execute the SQL statement
                cursor.execute(insert_sql, values)
            except Exception as e:
                upload_summary["messages"].append({"text": f"Temporary Table Insertion Error (row {rownum}): {e}", "message_type": "error"})

        cursor.execute("SELECT * FROM temp_table")
        rows = cursor.fetchall()

        check_problem_sql = 'SELECT id FROM benchmarks_problem WHERE name like %s'
        insert_problem_sql = 'INSERT INTO benchmarks_problem(name, url1, notes) values (%s, %s, %s)'
        
        check_graph_sql = 'SELECT id FROM benchmarks_graph WHERE name like %s'
        insert_graph_sql = 'INSERT INTO benchmarks_graph(name, url1, notes) values (%s, %s, %s)'
        
        check_instance_sql = '''
        SELECT id
        FROM benchmarks_probleminstance
        WHERE problem_id = %s
        and graph_id = %s
        and (graph_size = %s OR (%s is NULL and graph_size is NULL))
        '''
        insert_instance_sql = '''
            INSERT INTO benchmarks_probleminstance (problem_id, graph_id, graph_size, url1, notes)
            VALUES (%s, %s, %s, %s, %s)
        '''
        
        insertions = {"problem_instances": 0, "problems": 0, "graphs": 0}
        for row in rows:
            # Here, you can process each row and use the variables as needed
            problem = row[0]
            graphsize = row[1]
            graphtype = row[2]
            url = row[3]
            note = row[4]
            rownum = row[5]

            # TODO: row_summary = {'Problem': problem, 'Graph Size': graphsize, 'Graph Type': graphtype, 'url': url, 'Notes': note}
            problem_id = None
            graph_id = None
            

            # Problem Foreign Key
            cursor.execute(check_problem_sql, [problem])
            check = cursor.fetchall()

            if len(check) == 0: # insert new problems into problem table
                cursor.execute(insert_problem_sql, (problem, url, note))
                upload_summary["messages"].append({"text": f"New Problem (row {rownum}): {problem}", "message_type": "success"})
                connection.commit()
                insertions["problems"] += 1
            
            cursor.execute(check_problem_sql, [problem])
            problem_get_id = cursor.fetchall()
            if problem_get_id: # foreign key correctly found
                problem_id = problem_get_id[0][0]
            else: # cannot insert entry due to foreign key error
                upload_summary["messages"].append({"text": f"Insertion Error (row {rownum}): Problem {problem} was not found after insertion.", "message_type": "error"})
                continue


            # Graph Foreign Key
            cursor.execute(check_graph_sql, (graphtype,))
            check = cursor.fetchall()

            if len(check) == 0: # insert new graphs into graph table
                cursor.execute(insert_graph_sql, (graphtype, url, note))
                upload_summary["messages"].append({"text": f"New Graph (row {rownum}): {graphtype}", "message_type": "success"})
                connection.commit()
                insertions["graphs"] += 1
            
            cursor.execute(check_graph_sql, (graphtype,))
            graph_get_id = cursor.fetchall()
            if graph_get_id: # foreign key correctly found
                graph_id = graph_get_id[0][0]
            else: # cannot insert entry due to foreign key error
                upload_summary["messages"].append({"text": f"Insertion Error (row {rownum}): Graph {graphtype} was not found after insertion.", "message_type": "error"})
                continue


            # Problem Instance
            # Check if the record exists
            cursor.execute(check_instance_sql, (problem_id, graph_id, graphsize, graphsize))
            check = cursor.fetchall()

            if len(check) > 0:
                upload_summary["messages"].append({"text": f"Exception (row {rownum}): Entry already exists in Problem Instances table", "message_type": "exception"})
                continue
            
            # Insert new record
            cursor.execute(insert_instance_sql, (problem_id, graph_id, graphsize, url, note))
            # TODO: print(f"New Problem Instance: {row_summary}")
            connection.commit()
                
            # Validate that entry was inserted
            cursor.execute(check_instance_sql, (problem_id, graph_id, graphsize, graphsize))
            instance_get_id = cursor.fetchall()
            
            if instance_get_id:
                instance_id = instance_get_id[0][0]
                insertions["problem_instances"] += 1
            else:
                upload_summary["messages"].append({"text": f"Insertion Error (row {rownum}): Problem instance could not be found after insertion", "message_type": "error"})

    upload_summary["top_message"] = f"Upload Summary: {df.shape[0]} rows read, {insertions['problem_instances']} problem instances inserted"
    if insertions["problems"]:
        upload_summary["top_message"] += f", {insertions['problems']} new problems"
    if insertions["graphs"]:
        upload_summary["top_message"] += f", {insertions['graphs']} new graphs"
    return upload_summary
