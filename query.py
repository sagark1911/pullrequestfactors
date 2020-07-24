import json
import datetime
import requests
import time
import pickle

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

# These are the criteria for repo selection:
#     - Min One closed pull request
#     - Not a fork
#     - Min 3 open issues
#     - Min 3 watchers
#     - Min 3 forks

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
    n_records = 0
    validRepository = {}
    for a in range(number_of_days):
        for hr in range(24):
            myDate = str(x.year) + '-' + string_dates(x.month) + '-' + string_dates(x.day) + '-' + str(hr)
            fileLocation = DATA_FOLDER + myDate + J_EXTENSION
            print(myDate)
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
            if len(validRepository)%500 == 1:
                print('Number of repos found : ' + str(len(validRepository)) + '\n' + str(validRepository))
                print("time elapsed: {:.2f}s".format(time.time() - start_time))
        x += datetime.timedelta(days=1)

    print(validRepository)
    print("Number of valid repositories in " + str(number_of_days) + " days is " + str(len(validRepository)))
    print("Number of corresponding total pull requests : " + str(sum(validRepository.values())))
    with open(save_path, "w") as fp:
        fp.write(json.dumps(validRepository))


def generatePRDataset(datetime_date, number_of_days, repo_path):
    x = datetime_date
    fp_repo = open(repo_path, 'r')
    repo_dict = json.loads(fp_repo.read())
    #print(repo_dict)
    #print(str(sum(repo_dict.values())))
    records = []
    for a in range(number_of_days):
        for hr in range(24):
            myDate = str(x.year) + '-' + string_dates(x.month) + '-' + string_dates(x.day) + '-' + str(hr)
            fileLocation = DATA_FOLDER + myDate + J_EXTENSION
            print(myDate)
            try:
                with open(fileLocation, encoding="utf8") as json_file:
                    for json_record in json_file.readlines():
                        data = json.loads(json_record)
                        if data['repo']['id'] in repo_dict:
                            records.append(create_record(data))
            except FileNotFoundError:
                print(fileLocation + ' : This file does not seem to exist.')
            except Exception:
                prettyPrint(data)
                raise('Something went wrong. ' + Exception.args[1])
        x += datetime.timedelta(days=1)
    fp_repo.close()



# Need to generate a list  [TestIncluded, CommitSize, No_of_Files_Changes,
#                           Social_distance, Prior_interaction, No_of_Comments,
#                           No_of_followers_Submitter, Submitter_Status, Repository_age,
#                           No_of_Collaborators, No_of_Stars, PR_Decision]
def create_record(record):

    # commitInfo(record) takes 2 API requests
    testIncluded , commitSize, filesChanged = commitInfo(record)
    #




start_time = time.time()
start_date = datetime.datetime(2015,1,1)
# events, n_records = explore(start_date, 15)
# print(events)
# print('Number of records: ' + str(n_records))
#generateRepoList(start_date, 10, "10_days_repoList" + J_EXTENSION)
generatePRDataset(start_date, 10, "10_days_repoList" + J_EXTENSION)
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