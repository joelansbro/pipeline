import requests
from pipe_utils import parquet_name

project = "None"

res = requests.get('http://localhost:5000/outbound/get_report/{}'.format(project))

if res.ok:
    output_name = '{}.csv'.format(parquet_name())
    with open(output_name, "w") as csv_file:
        csv_file.write(str(res.content))