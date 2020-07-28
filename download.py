import requests
import gzip
import datetime
import time

BASE_URL = 'https://data.gharchive.org/'
DOWNLOAD_BASE_PATH = 'D:\\CS846-Mei\\Project\\data\\'
COMPRESSED_FOLDER = 'compressed\\'
DECOMPRESSED_FOLDER = 'decompressed\\'
D_EXTENSION = '.json.gz'
J_EXTENSION = '.json'

def download_url(url, save_path, chunk_size=128):
    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)

def unzip(gzip_path, save_path):
    input = gzip.GzipFile(gzip_path, 'rb')
    s = input.read()
    input.close()
    output = open(save_path, 'wb')
    output.write(s)
    output.close()

def string_dates(x):
    if x < 10:
        return '0' + str(x)
    else:
        return str(x)

def download_archive(datetime_start_date, number_of_days):
    x = datetime_start_date
    if number_of_days < 1:
        return
    start_time = time.time()
    for a in range(number_of_days):
        for hr in range(24):
            myDate = str(x.year) + '-' + string_dates(x.month) + '-' + string_dates(x.day) + '-' + str(hr)
            download_url(BASE_URL + myDate + D_EXTENSION, DOWNLOAD_BASE_PATH + COMPRESSED_FOLDER + myDate + D_EXTENSION)
            unzip(DOWNLOAD_BASE_PATH + COMPRESSED_FOLDER + myDate+D_EXTENSION, DOWNLOAD_BASE_PATH+ DECOMPRESSED_FOLDER +myDate+J_EXTENSION)
        print('Downloaded: ' + str(x))
        print("time elapsed: {:.2f}s".format(time.time() - start_time))
        x = x + datetime.timedelta(days=1)

start_date = datetime.datetime(2015, 1, 1)
download_archive(start_date, 1)
# for a in range(40):
#     for hr in range(24):
#         myDate = str(x.year) + '-' + string_dates(x.month) + '-' + string_dates(x.day) + '-' + str(hr)
#         print(myDate)
#    x = x + datetime.timedelta(days=1)

#download_url(BASE_URL+date+D_EXTENSION, DOWNLOAD_BASE_PATH+'compressed\\'+date+D_EXTENSION)
#unzip(DOWNLOAD_BASE_PATH+'compressed\\'+date+D_EXTENSION, DOWNLOAD_BASE_PATH+'decompressed\\' +date+J_EXTENSION)