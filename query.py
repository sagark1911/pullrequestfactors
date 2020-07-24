import json
import datetime
import requests
import time

api_requests = 0

DOWNLOAD_BASE_PATH = 'D:\\CS846-Mei\\Project\\data\\'
DECOMPRESSED_FOLDER = 'decompressed\\'
DATA_FOLDER = DOWNLOAD_BASE_PATH + DECOMPRESSED_FOLDER
J_EXTENSION = '.json'
USERNAME = 'sagark1911'
try:
    with open('D:\\CS846-Mei\\Project\\Personal-access-token.txt', 'r') as f:
        API_TOKEN = f.read()
except Exception:
    print("File not found")
    raise

def string_dates(x):
    if x < 10:
        return '0' + str(x)
    else:
        return str(x)

def prettyPrint(json_object):
    print(json.dumps(json_object, indent=4))

def external_request(url):
    global api_requests
    api_requests = api_requests + 1
    response = requests.get(url, auth=(USERNAME, API_TOKEN))
    if response.ok:
        pass
    else:

        print("Api limit may have crossed(5000 per hour)! Total API requests = " + api_requests)
    return response

def rate_limit():
    response = requests.get('https://api.github.com/rate_limit', auth=(USERNAME, API_TOKEN))
    print(response.json()['rate'])

def explore(datetime_start_date, number_of_days):
    x = datetime_start_date
    events = {}
    #records = []
    n_records = 0
    pull_request_events = []
    for a in range(number_of_days):
        for hr in range(24):
            myDate = str(x.year) + '-' + string_dates(x.month) + '-' + string_dates(x.day) + '-' + str(hr)
            fileLocation = DATA_FOLDER + myDate + J_EXTENSION
            print(fileLocation)
            try:
                with open(fileLocation, encoding="utf8") as json_file:
                    for json_record in json_file.readlines():
                        n_records += 1
                        data = json.loads(json_record)
                        #records.append(data)
                        if data['type'] == 'PullRequestEvent':
                            if data['payload']['pull_request']['merged'] == True:
                                print('merged : True')
                                if data['payload']['pull_request']['user']['site_admin'] == True:
                                    prettyPrint(data)
                                    exit(42)
                            #print('merged: ' + str(data['payload']['pull_request']['merged']))
                        if data['type'] not in events:
                            events[data['type']] = 1
                            #print(json.dumps(data, indent=2))
                        else:
                            events[data['type']] = events[data['type']] + 1
            except FileNotFoundError:
                print(fileLocation + ' : This file does not seem to exist.')
            except TypeError:
                print()
            except Exception:
                prettyPrint(data)
                raise('Something went wrong. ' + Exception.args[1])

        x += datetime.timedelta(days=1)
    return events, n_records


def


start_time = time.time()
start_date = datetime.datetime(2015,1,1)
events, n_records = explore(start_date, 15)
print(events)
print('Number of records: ' + str(n_records))
print("time elapsed: {:.2f}s".format(time.time() - start_time))
rate_limit()

# for a in range(100):
#     response = external_request('https://api.github.com/users/phxql/followers')
#     if response.ok:
#         print("Response : " + str(a) + " okay!")
#     else:
#         print(response.text)
# print(api_requests)
#print(response.text)