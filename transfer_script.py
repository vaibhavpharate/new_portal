import boto3
import pandas as pd
from sqlalchemy import text, create_engine
from datetime import datetime, timedelta
import os

## AWS BUCKETS CONFIG
AWS_KEY = 'AKIASX6C3Q3MP735NPEB'
AWS_PASS = 'rAYfnBhmt+tRt2jMR1lCbRFOUglEglutyxY8Q33H'
BUCKET_NAME = 'gif-buckets'
GIF_S3_FOLDER = 'gif'
FRAME_S3_FOLDER = 'LATEST_FRAME'

MEDIA_PATH = "/home/ubuntu/vaib/new_portal/media"
# MEDIA_PATH = "/home/ubuntu/vaib/Haliware/Frontend/dark_website/media"
GIF_MAIN_PATH = f"{MEDIA_PATH}/GIF"
Frame_MAIN_PATH = f"{MEDIA_PATH}/Frame"
CSV_PATH = f"{MEDIA_PATH}/weather_data"

conn_dict = {'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'admin123',
        'PASSWORD': 'tensor123',
        'HOST': 'tensordb1.cn6gzof6sqbw.us-east-2.rds.amazonaws.com',
        'PORT': '5432',}

## create the connection engine
def get_connection(host,port,user,passord,database):
    connection_string = f"postgresql://{user}:{passord}@{host}/{database}"
    db_connect = create_engine(connection_string)
    try:
        with db_connect.connect() as con:
            con.execute(text("SELECT 1"))
            print("\n\n---------------------Connection Successful")
        return db_connect
    except Exception as e:
        print(e)
        print("\n\n---------------------Connection Failed")

## create S3 client
def get_s3_client(access_key,access_pass):
    s3_client = boto3.client('s3', aws_access_key_id=f'{access_key}',
                         aws_secret_access_key=f'{access_pass}')
    return s3_client


db_connection = get_connection(host = conn_dict['HOST'],
                              port = conn_dict['PORT'],
                              user = conn_dict['USER'],
                              passord=conn_dict['PASSWORD'],
                              database=conn_dict['NAME'])

s3_client = get_s3_client(access_key=AWS_KEY,access_pass=AWS_PASS)


## check GIF available in s3
def check_file_exists_s3(file_name,bucket_name,s3_client):
    file_count = s3_client.list_objects_v2(Bucket=bucket_name,
                                           Prefix=f'{file_name}')['KeyCount']
    if file_count == 0:
        return False
    elif file_count > 0:
        return True


## check for the gif in s3
def get_the_latest_gif_data(db_connection):
    df = pd.read_sql_query("SELECT * FROM file_logs.gif_created order by timestamp desc limit 1",db_connection)
    return df

# 20240229T123000.gif

## create a transfer function
def transfer_s3_gif(s3_client,db_connection):
    gif_timestamp_format = "%Y%m%dT%H%M%S.gif"

    df = get_the_latest_gif_data(db_connection=db_connection)
    latest_timestamp_file = df['timestamp'][0]
    latest_timestamp = latest_timestamp_file
    last_3_hours = latest_timestamp - timedelta(hours=3)

    ## check for any gifs that are there for more than 3  hours
    old_gifs = os.listdir(GIF_MAIN_PATH)
    for x in old_gifs:
        # convert files to datetime
        if x !='sample.txt':
            file_timestamp = datetime.strptime(x,gif_timestamp_format)
            if file_timestamp <= last_3_hours:
                os.remove(f"{GIF_MAIN_PATH}/{x}")
                print(f"Removed gif {x}")

    # print(old_gifs)
    s3_file_link = df['s3_link'][0]
    response_gif = check_file_exists_s3(file_name=s3_file_link,bucket_name=BUCKET_NAME,s3_client=s3_client)
    if response_gif:
        file_name = s3_file_link[4:]
        # download and transfer file from s3 to dashboard folder
        print(f'{GIF_MAIN_PATH}/{file_name}')
        if os.path.exists(f'{GIF_MAIN_PATH}/{file_name}') == False:
            print(file_name)
            s3_client.download_file('gif-buckets',f'{s3_file_link}',f'{GIF_MAIN_PATH}/{file_name}')
            print("GIF FILE TRANSFERRED SUCCESSFULLY")
            ## Perform a database confirmation function
        else:
            print("GIF already transferred to the dashboard location")
    else:
        print("FILE NOT AVAILABLE ON S3")


## check for the frames in s3
def get_the_latest_frames_data(db_connection):
    df = pd.read_sql_query("SELECT * FROM file_logs.frame_updates order by timestamp desc limit 1",db_connection)
    return df


def transfer_s3_frame(s3_client,db_connection):
    gif_timestamp_format = "%Y%m%dT%H%M%S.png"
    df = get_the_latest_frames_data(db_connection=db_connection)
    latest_timestamp_file = df['timestamp'][0]
    latest_timestamp = latest_timestamp_file
    last_3_hours = latest_timestamp - timedelta(hours=3)

    ## check for any gifs that are there for more than 3  hours
    old_gifs = os.listdir(Frame_MAIN_PATH)
    for x in old_gifs:
        # convert files to datetime
        if x !='sample.txt':
            file_timestamp = datetime.strptime(x,gif_timestamp_format)
            if file_timestamp <= last_3_hours:
                os.remove(f"{Frame_MAIN_PATH}/{x}")
                print(f"Removed Frame {x}")

    s3_file_link = df['s3_link'][0]
    response_gif = check_file_exists_s3(file_name=s3_file_link,bucket_name=BUCKET_NAME,s3_client=s3_client)
    if response_gif:
        file_name = s3_file_link[13:]
        # download and transfer file from s3 to dashboard folder
        if os.path.exists(f'{Frame_MAIN_PATH}/{file_name}') == False:
            s3_client.download_file('gif-buckets',f'{s3_file_link}',f'{Frame_MAIN_PATH}/{file_name}')
            print("FRAME FILE TRANSFERRED SUCCESSFULLY")
            ## Perform a database confirmation function
        else:
            print("FRAME already transferred to the dashboard location")
    else:
        print("FILE NOT AVAILABLE ON S3")

def transfer_csv(s3_client,db_connection):
    csv_format = "%Y-%m-%dT%H%M%S_erv.csv"
    df = pd.read_sql_query("SELECT * FROM file_logs.s3_csv order by timestamp desc limit 1",db_connection)
    latest_timestamp_file = df['timestamp'][0]
    latest_timestamp = latest_timestamp_file
    last_3_hours = latest_timestamp - timedelta(hours=3)
    folder_date = latest_timestamp_file.strftime('%Y%m%d')
    old_csvs = os.listdir(CSV_PATH)
    for x in old_csvs:
        # convert files to datetime
        if x !='sample.txt':
            file_timestamp = datetime.strptime(x,csv_format)
            if file_timestamp <= last_3_hours:
                os.remove(f"{CSV_PATH}/{x}")
                print(f"Removed Frame {x}")
    s3_file_link = df['s3_link'][0]
    file_name = s3_file_link[19:]
    print(file_name)
    s3_client.download_file('gif-buckets',f'{s3_file_link}',f'{CSV_PATH}/{file_name}')
    print("CSV FILE TRANSFERRED SUCCESSFULLY")

transfer_s3_gif(s3_client=s3_client,db_connection=db_connection)
transfer_s3_frame(s3_client=s3_client,db_connection=db_connection)
transfer_csv(s3_client=s3_client,db_connection=db_connection)
