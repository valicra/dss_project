# -*- coding: utf-8 -*-

import csv
import pyodbc 

# Function 'data_load_CSV': this function describes how to retrieve data from the .csv we have
def data_load_CSV(file_path, table_name, connection_string):

    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()
    cursor.fast_executemany=True

    with open(file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        header = csv_reader.fieldnames
        data = [tuple(row.values()) for row in csv_reader]


    placeholders = ', '.join(['?' for _ in header])
    sql_query = f"INSERT INTO {table_name} ({', '.join(header)}) VALUES ({placeholders})"

    cursor.executemany(sql_query, data)

    connection.commit()

    cursor.close()
    connection.close()


if __name__ == "__main__":

    # connection parameters and credentials
    server = 'tcp:lds.di.unipi.it' 
    database = 'Group_ID_781_DB'
    username = 'Group_ID_781'
    password = '3YJD1IYAE'
    connection_string = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password
    
    # loading data and populating all the tables
    try: 
        # starting loading all the dimension table 
        data_load_CSV('./Time.csv', 'time', connection_string)

        data_load_CSV('./Cpu.csv', 'cpu', connection_string)

        data_load_CSV('./Geo.csv', 'geography', connection_string)

        data_load_CSV('./Ram.csv', 'ram', connection_string)    

        data_load_CSV('./Gpu.csv', 'gpu', connection_string)

        # the fact tale must be loaded and populated as last table, in order to correctly import the foreign keys
        data_load_CSV('./fact.csv', 'computer_sales', connection_string)
        
    except Exception as e:
        print("error in the overall process")
