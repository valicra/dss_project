import csv
from datetime import datetime, date
from currency_converter import CurrencyConverter


def make_geo(main_file, geo_file, output_file, geo_attributes):

    with (
        open(main_file, 'r') as main,
        open(geo_file, 'r') as geo, 
        open(output_file, 'w', newline='') as out):

        reader_main = csv.DictReader(main)
        reader_geo = csv.DictReader(geo)
        writer = csv.writer(out)

        writer.writerow(geo_attributes)

        writer = csv.DictWriter(out, geo_attributes)

        currency_map = dict()

        for row in reader_main:
            if row['geo_id'] not in currency_map:
                currency_map[row['geo_id']] = row['currency']

        for row in reader_geo:
            row.update({'currency': currency_map[row['geo_id']]})
            writer.writerow(row) 


def get_time(time_code):

    day = int(time_code[-2:])
    month = int(time_code[-4:-2])
    year = int(time_code[:4])

    date = datetime(year, month, day).isoweekday()

    if date == 1:
        day_of_week = 'Monday'
    elif date == 2:
        day_of_week = 'Tuesday'
    elif date == 3:
        day_of_week = 'Wednesday'
    elif date == 4:
        day_of_week = 'Thursday'
    elif date == 5:
        day_of_week = 'Friday'
    elif date == 6:
        day_of_week = 'Saturday'
    else:
        day_of_week = 'Sunday'

    if day / 7 <= 1 :
        week = 'Week1'
    elif (1 < day / 7 <= 2 ) :
        week = 'Week2'
    elif (2 < day / 7 <= 3 ) :
        week = 'Week3'
    else:
        week = 'Week4'

    if month / 3 <= 1 :
        q = 'q1'
    elif (1 < month / 3 <= 2 ) :
        q = 'q2'
    elif (2 < month / 3 <= 3 ) :
        q = 'q3'
    else:
        q = 'q4'


    d = {'date': str(year)+'-'+str(month)+'-'+str(day), 
        'day': str(day),
        'day_of_week': day_of_week, 
        'week': week,
        'month': str(month),
        'quarter': q,
        'year' : str(year)}
    
    return d


def make_time(input_file, output_file, time_attributes):

    with (
        open(input_file, 'r') as file,
        open(output_file, 'w', newline='') as out
    ):

        reader = csv.DictReader(file)
        writer = csv.writer(out)

        writer.writerow(time_attributes)

        writer = csv.DictWriter(out, time_attributes)

        unique_times = set()

        for row in reader :
            
            unique_times.add(row['time_code'])
            
        i=0
        for time_code in unique_times:  
            d = get_time(time_code)
            d['time_id'] = i 
            writer.writerow(d)
            i+=1


def make_fact(input_file, fact_file, fact_attributes):
    with (
        open(input_file, 'r') as file,
        open(fact_file, 'w', newline='') as fact
    ):
        reader = csv.DictReader(file)
       
        writer_fact = csv.writer(fact)
        writer_fact.writerow(fact_attributes)
        writer_fact = csv.DictWriter(fact, fact_attributes)

        c = CurrencyConverter(fallback_on_missing_rate=True, fallback_on_missing_rate_method='last_known')


        for row in reader:
            given_date = get_time(row['time_code'])
            
            tow_fact = {
                'ram_sales': row['ram_sales_currency'],
                'ram_sales_usd' : round(c.convert(row['ram_sales_currency'], row['currency'], 'USD', date(int(given_date['year']), int(given_date['month']), int(given_date['day']))), 2),
                'cpu_sales': row['cpu_sales_currency'],
                'cpu_sales_usd' : round(c.convert(row['cpu_sales_currency'], row['currency'], 'USD', date(int(given_date['year']), int(given_date['month']), int(given_date['day']))), 2),
                'gpu_sales' : row['gpu_sales_currency'],
                'gpu_sales_usd' : round(c.convert(row['gpu_sales_currency'], row['currency'], 'USD', date(int(given_date['year']), int(given_date['month']), int(given_date['day']))), 2),
                'total_sales' : row['sales_currency'],
                'total_sales_usd': round(c.convert(row['sales_currency'], row['currency'], 'USD', date(int(given_date['year']), int(given_date['month']), int(given_date['day']))), 2),
                }
            
            writer_fact.writerow(tow_fact)


def make_dim(input_file, output_file, attributes):
    
    with (
        open(input_file, 'r') as file,
        open(output_file, 'w', newline='') as out
        ):

        reader = csv.DictReader(file)
        writer = csv.writer(out)
        id_to_add = input_file.split('.')[0].lower()+'_id'
        writer.writerow([id_to_add] + attributes)

        unique_rows_no_id = set()
        unique_rows_with_id = set()

        i=0
        for row in reader:
            filtered_row = [row[attr] for attr in attributes]
            if filtered_row not in unique_rows_no_id:
                filtered_row.insert(0, i)
                unique_rows_with_id.add(filtered_row)
                i+=1


        for row in unique_rows_with_id:
            writer.writerow(row)



if __name__ == '__main__':

    ram_attr = ['ram_vendor_name', 'ram_brand', 'ram_name', 'ram_size', 'ram_type', 'ram_clock']
    fact_attr = ['ram_sales', 'ram_sales_usd', 'cpu_sales', 'cpu_sales_usd', 'gpu_sales', 'gpu_sales_usd', 'total_sales', 'total_sales_usd']
    geo_attr = ['geo_id', 'country', 'region', 'continent', 'currency']
    time_attr = ['time_id', 'date', 'day','day_of_week','week', 'month','quarter', 'year']
    cpu_attr = ['cpu_vendor_name', 'cpu_brand', 'cpu_series', 'cpu_name', 'cpu_n_cores', 'cpu_socket']
    gpu_attr = ['gpu_vendor_name', 'gpu_brand', 'gpu_processor_manufacturer', 'gpu_memory', 'gpu_memory_type']

    make_fact('computer_sales.csv', 'fact.csv', fact_attr)
    make_time('computer_sales.csv', 'Time_with_id.csv', time_attr)
    make_geo('computer_sales.csv', 'geography.csv', 'Geo.csv', geo_attr )
    make_dim('computer_sales.csv', 'Cpu.csv', cpu_attr)
    make_dim('computer_sales.csv', 'Gpu.csv', gpu_attr)
    make_dim('computer_sales.csv', 'Ram.csv', ram_attr)