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
        rate_limit()
    return response

def rate_limit():
    response = requests.get('https://api.github.com/rate_limit', auth=(USERNAME, API_TOKEN))
    print(response.json()['rate'])

def explore(datetime_start_date, number_of_days):
    x = datetime_start_date
    events = {}
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

# These are the criteria for repo selection:
#     - Min One closed pull request
#     - Not a fork
#     - Min 3 open issues
#     - Min 3 watchers
#     - Min 3 forks

# def isValidRepo(repo):
#     response = external_request(repo['url'])
#     if not response.ok :
#         return False
#         #prettyPrint("REPO : \n" + str(response.json()))
#     repo_json = response.json()
#     # Some repositories do not exist anymore
#     if 'message' in repo_json:
#         if repo_json['message'] == 'Not Found':
#             return False
#     # No forks
#     if repo_json['fork'] == 'true':
#         return False
#     # Min 3 open issues
#     if repo_json["open_issues_count"] < 3:
#         return False
#     # Min 3 contributors
#     response2 = external_request(repo_json['contributors_url'])
#     number_of_contributors = len(response2.json())
#     if number_of_contributors < 3:
#         return False
#     # great, now this is valid
#     return True

def isValidRepo(repo):
    repo_json = repo['payload']['pull_request']['base']['repo']
    if repo_json['fork'] == 'true':
        return False
    if repo_json["open_issues_count"] < 3:
        return False
    if repo_json['watchers_count'] < 3:
        return False
    if repo_json['forks_count'] < 3:
        return False
    # great, now this is valid
    return True

# Generate a list of repositories that meet the selection criteria
def generateRepoList(datetime_date, number_of_days, save_path):
    x = datetime_date
    events = {}
    n_records = 0
    validRepository = {}
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
                        if data['type'] == 'PullRequestEvent':
                            if data['payload']['action'] == 'closed':
                                #prettyPrint(data)
                                if data['repo']['id'] in validRepository:
                                    validRepository[data['repo']['id']] = validRepository[data['repo']['id']] + 1
                                elif isValidRepo(data):
                                        validRepository[data['repo']['id']] = 1
                                else:
                                    continue
            except FileNotFoundError:
                print(fileLocation + ' : This file does not seem to exist.')
            except Exception:
                prettyPrint(data)
                raise('Something went wrong. ' + Exception.args[1])
            if len(validRepository)%30 == 1:
                print('Number of repos found : ' + str(len(validRepository)) + '\n' + str(validRepository))
                print("time elapsed: {:.2f}s".format(time.time() - start_time))
    print(validRepository)
    print("Number of valid repositories in " + str(number_of_days) + " days is " + str(len(validRepository)))



# Need to generate a list  [TestIncluded, CommitSize, No_of_Files_Changes,
#                           Social_distance, Prior_interaction, No_of_Comments,
#                           No_of_followers_Submitter, Submitter_Status, Repository_age,
#                           No_of_Collaborators, No_of_Stars]
def create_record(record):
    # commitInfo(record) takes 2 API requests
    testIncluded , commitSize, filesChanged = commitInfo(record)
    #




start_time = time.time()
start_date = datetime.datetime(2015,1,1)
# events, n_records = explore(start_date, 15)
# print(events)
# print('Number of records: ' + str(n_records))
generateRepoList(start_date, 1, "blah blah")
rate_limit()
print("time elapsed: {:.2f}s".format(time.time() - start_time))

# for a in range(100):
#     response = external_request('https://api.github.com/users/phxql/followers')
#     if response.ok:
#         print("Response : " + str(a) + " okay!")
#     else:
#         print(response.text)
# print(api_requests)
#print(response.text)