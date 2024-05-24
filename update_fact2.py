# this script updates the fact table with foreign keys


import csv
from assigment1 import get_time
from datetime import date
from currency_converter import CurrencyConverter

def add_fks(cs_file, time_file, cpu_file, gpu_file, ram_file, output_file):
    
    def read_file_into_dict(file_path, key_field):
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            return {tuple(row[field] for field in reader.fieldnames if field != key_field): row[key_field] for row in reader}, reader.fieldnames

    # Read all reference files into dictionaries
    ram_dict, ram_fields = read_file_into_dict(ram_file, 'ram_id')
    cpu_dict, cpu_fields = read_file_into_dict(cpu_file, 'cpu_id')
    gpu_dict, gpu_fields = read_file_into_dict(gpu_file, 'gpu_id')
    time_dict, time_fields = read_file_into_dict(time_file, 'time_id')

    ram_fields.remove('ram_id')
    cpu_fields.remove('cpu_id')
    gpu_fields.remove('gpu_id')
    time_fields.remove('time_id')

    with open(cs_file, 'r') as cs_table, open(output_file, 'w', newline='') as output:
        reader_cs = csv.DictReader(cs_table)

        writer = csv.writer(output)
        fact_header = ['geo_id', 'time_id', 'cpu_id', 'gpu_id', 'ram_id','ram_sales', 
                       'ram_sales_usd', 'cpu_sales', 'cpu_sales_usd', 'gpu_sales', 'gpu_sales_usd', 'total_sales', 'total_sales_usd']
        writer.writerow(fact_header)
        writer = csv.DictWriter(output, fact_header)
        
        c = CurrencyConverter(fallback_on_missing_rate=True, fallback_on_missing_rate_method='last_known')
        
        for row_cs in reader_cs:
            to_write = dict()

            ram_row = tuple(row_cs[attr] for attr in ram_fields)
            cpu_row = tuple(row_cs[attr] for attr in cpu_fields)
            gpu_row = tuple(row_cs[attr] for attr in gpu_fields)
            time_row = tuple(get_time(row_cs['time_code']).values())

            ram_id = ram_dict.get(ram_row)
            if ram_id:
                to_write.update({'ram_id': ram_id})
                
            cpu_id = cpu_dict.get(cpu_row)
            if cpu_id:
                to_write.update({'cpu_id': cpu_id})
                
            gpu_id = gpu_dict.get(gpu_row)
            if gpu_id:
                to_write.update({'gpu_id': gpu_id})
                
            time_id = time_dict.get(time_row)
            if time_id:
                to_write.update({'time_id': time_id})
                
            given_date = get_time(row_cs['time_code'])
            
            to_write.update({
                'geo_id': row_cs['geo_id'],
                'ram_sales': row_cs['ram_sales_currency'],
                'ram_sales_usd': round(c.convert(row_cs['ram_sales_currency'], row_cs['currency'], 'USD', date(int(given_date['year']), int(given_date['month']), int(given_date['day']))), 2),
                'cpu_sales': row_cs['cpu_sales_currency'],
                'cpu_sales_usd': round(c.convert(row_cs['cpu_sales_currency'], row_cs['currency'], 'USD', date(int(given_date['year']), int(given_date['month']), int(given_date['day']))), 2),
                'gpu_sales': row_cs['gpu_sales_currency'],
                'gpu_sales_usd': round(c.convert(row_cs['gpu_sales_currency'], row_cs['currency'], 'USD', date(int(given_date['year']), int(given_date['month']), int(given_date['day']))), 2),
                'total_sales': row_cs['sales_currency'],
                'total_sales_usd': round(c.convert(row_cs['sales_currency'], row_cs['currency'], 'USD', date(int(given_date['year']), int(given_date['month']), int(given_date['day']))), 2),
            })
            
            writer.writerow(to_write)


if __name__=='__main__':

    add_fks('computer_sales.csv', 'Time_with_id.csv', 'Cpu_with_id.csv',
            'Gpu_with_id.csv',
            'Ram_with_id.csv',
            'Fact_with_id.csv')