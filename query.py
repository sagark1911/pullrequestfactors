import json
import datetime
import requests
import time
import pandas as pd
api_requests = 0

API_LIMIT = 20

RESET_TIME = 10

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
    while rate_remaining() < 10:
        print("going to sleep for an 20sec and check again")
        time.sleep(20)
    response = ''
    while response == '':
        try:
            response = requests.get(url, auth=(USERNAME, API_TOKEN))
            break
        except:
            print("Connection refused by the server for external_request()..")
            print("Let me sleep for 30 seconds")
            print("ZZzzzz...")
            time.sleep(30)
            print("Was a nice sleep, now let me continue...")
            continue
    return response

def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError as e:
    return False
  return True

def rate_remaining():
    page = ''
    while page == '':
        try:
            page = requests.get('https://api.github.com/rate_limit', auth=(USERNAME, API_TOKEN))
            break
        except:
            print("Connection refused by the server to check rate limit..")
            print("Let me sleep for 30 seconds")
            print("ZZzzzz...")
            time.sleep(30)
            print("Was a nice sleep, now let me continue...")
            continue

    return page.json()['rate']['remaining']

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

def save_records(records, extension):
    columns = ['PRBodySize', 'CommitSize', 'No_of_Files_Changed', 'socialDistance', 'No_of_Comments', 'timeSpentOnPR', 'repositoryAge','No_of_collaborators', 'No_of_Stars', 'No_of_Watchers', 'No_of_OpenIssues', 'No_of_followers_Submitter', 'submitterStatus', 'pullrequestDecision']
    df = pd.DataFrame.from_records(records, columns=columns)
    df.to_csv('trial-dataset\\' + 'records-'+ extension + '.csv')


def generatePRDataset(datetime_date, number_of_days, repo_list_filepath):
    x = datetime_date
    fp_repo = open(repo_list_filepath, 'r')
    repo_dict = json.loads(fp_repo.read())
    # print(len(repo_dict))
    # print(str(sum(repo_dict.values())))
    # exit(42)
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
                        #print(data)
                        #exit(42)
                        if str(data['repo']['id']) in repo_dict:
                            #print("Repo is a match")
                            if data['type'] == 'PullRequestEvent' and data['payload']['action'] == 'closed':
                                # We can ignore cases where user closes their own pull request
                                if data['payload']['pull_request']['user'] != None:
                                    if data['payload']['pull_request']['base']['repo']['fork'] == True:
                                        continue
                                    if data['actor']['id'] == data['payload']['pull_request']['user']['id'] and data['payload']['pull_request']['merged'] == False:
                                        continue
                                    else:
                                        #print("Match")
                                        records.append(create_record(data))
                                        if len(records) % 20 == 1:
                                            print("time elapsed: {:.2f}s".format(time.time() - start_time))
                                            print('Rate limit remaining: ' + str(rate_remaining()))
            except FileNotFoundError:
                print(fileLocation + ' : This file does not seem to exist.')
            except Exception:
                prettyPrint(data)
                raise('Something went wrong. ' + Exception.args[1])
            save_records(records, myDate)
        x += datetime.timedelta(days=1)
    fp_repo.close()

# takes alot of API calls (depending on number of commits) not completing it for this version
def testsPresent(data):
    commits_url = data['payload']['pull_request']['commits_url']
    response = external_request(commits_url)


def technicalContribution(data):
    testIncluded = 0
    if data['payload']['pull_request']['body'] == None:
        PRBodySize = 0
    else:
        PRBodySize = len(data['payload']['pull_request']['body'])
    CommitSize = data['payload']['pull_request']['additions'] + data['payload']['pull_request']['deletions']
    No_of_Files_Changed = data['payload']['pull_request']['changed_files']
    return testIncluded, PRBodySize, CommitSize, No_of_Files_Changed

def sDistance(data):
    # followers of the person who closed the pull_request
    followers_url = data['actor']['url'] + '/followers'
    user = data['payload']['pull_request']['user']
    if user == None:
        return 0
    response = external_request(followers_url)
    if response.ok and is_json(response.text):
        followersList = response.json()
        for follower in followersList:
            if user == follower['login']:
                return 1
    else:
        return -1
    return 0

def socialConnection(data):
    # Seems to always return 0
    socialDistance = sDistance(data)
    # Need to implement prior interaction later
    priorInteraction = 0
    return socialDistance, priorInteraction

def pullrequestFeatures(data):
    #print('Review comments = ' + str(data['payload']['pull_request']['review_comments'])  + '\nComments = ' + str(data['payload']['pull_request']['comments']))
    No_of_Comments = data['payload']['pull_request']['review_comments'] + data['payload']['pull_request']['comments']
    if data['payload']['pull_request']['created_at'] == None or data['payload']['pull_request']['closed_at'] == None:
        timeSpentonPR = -1
    else:
        pullrequestCreatedTime =  datetime.datetime.strptime(data['payload']['pull_request']['created_at'], "%Y-%m-%dT%H:%M:%SZ")
        pullrequestClosedTime =  datetime.datetime.strptime(data['payload']['pull_request']['closed_at'], "%Y-%m-%dT%H:%M:%SZ")
        differenceDelta =  pullrequestClosedTime - pullrequestCreatedTime
        timeSpentonPR = differenceDelta.days

    return No_of_Comments, timeSpentonPR, data['payload']['pull_request']['created_at']

def repoFeatures(data, timePRcreated):
    if data['payload']['pull_request']['created_at'] == None or timePRcreated == None:
        repositoryAge = -1
    else:
        repo_created = datetime.datetime.strptime(data['payload']['pull_request']['base']['repo']['created_at'], "%Y-%m-%dT%H:%M:%SZ")
        pr_created = datetime.datetime.strptime(timePRcreated, "%Y-%m-%dT%H:%M:%SZ")
        repo_age_delta = pr_created - repo_created
        repositoryAge = repo_age_delta.days

    repo_contributors_url = data['payload']['pull_request']['base']['repo']['contributors_url']
    response = external_request(repo_contributors_url)
    if response.ok and is_json(response.text):
        repo_contributors_list = response.json()
        No_of_contributors = len(repo_contributors_list)
    else:
        No_of_contributors = -1
        repo_contributors_list = []
    No_of_Stars = data['payload']['pull_request']['base']['repo']['stargazers_count']
    No_of_Watchers = data['payload']['pull_request']['base']['repo']['watchers_count']
    No_of_OpenIssues = data['payload']['pull_request']['base']['repo']['open_issues_count']

    return repositoryAge, No_of_contributors, repo_contributors_list, No_of_Stars, No_of_Watchers, No_of_OpenIssues


def submitterFeatures(data, collaboratorList):
    user = data['payload']['pull_request']['user']
    No_of_followers_Submitter = 0
    if user == None:
        No_of_followers_Submitter = 0
    elif 'followers_url' in user:
        user_followers_url = user['followers_url']
        response = external_request(user_followers_url)
        if response.ok and is_json(response.text):
            user_followers = response.json()
            No_of_followers_Submitter = len(user_followers)
        else:
            No_of_followers_Submitter = -1

    submitterStatus = 0
    if user == None:
        submitterStatus = 0
    elif 'login' in user:
        for collaborator in collaboratorList:
            if user['login'] == collaborator['login']:
                submitterStatus = 1
    return No_of_followers_Submitter, submitterStatus

def isMerged(data):
    if data['payload']['pull_request']['merged'] == True:
        return 1
    else:
        return 0

# Need to generate a list  [TestIncluded, CommitSize, No_of_Files_Changes,
#                           Social_distance, Prior_interaction, No_of_Comments,
#                           No_of_followers_Submitter, Submitter_Status, Repository_age,
#                           No_of_Collaborators, No_of_Stars, PR_Decision]
def create_record(data):

    # technicalContribution(record) take a total 2 API calls
    testIncluded, PRBodySize, CommitSize, No_of_Files_Changed = technicalContribution(data)
    # socialConnection take a total of 2 API calls
    socialDistance, priorInteraction = socialConnection(data)
    # pullrequestFeatures take a total of 0 API calls
    No_of_Comments, timeSpentOnPR, timePRcreated = pullrequestFeatures(data)
    # repoFeatures take a total of 1 API calls
    repositoryAge, No_of_collaborators, collaboratorList, No_of_Stars, No_of_Watchers, No_of_OpenIssues = repoFeatures(data, timePRcreated)
    # submitterFeature takes a total of 1 API calls
    No_of_followers_Submitter, submitterStatus = submitterFeatures(data, collaboratorList)

    pullrequestDecision = isMerged(data)
    #print([PRBodySize, CommitSize, No_of_Files_Changed, socialDistance, No_of_Comments, timeSpentOnPR, repositoryAge, No_of_collaborators, No_of_Stars, No_of_Watchers, No_of_OpenIssues, No_of_followers_Submitter, submitterStatus, pullrequestDecision])
    return [PRBodySize, CommitSize, No_of_Files_Changed, socialDistance, No_of_Comments, timeSpentOnPR, repositoryAge, No_of_collaborators, No_of_Stars, No_of_Watchers, No_of_OpenIssues, No_of_followers_Submitter, submitterStatus, pullrequestDecision]



start_time = time.time()
start_date = datetime.datetime(2015,1,4)
# events, n_records = explore(start_date, 15)
# print(events)
# print('Number of records: ' + str(n_records))
#generateRepoList(start_date, 10, "10_days_repoList" + J_EXTENSION)
generatePRDataset(start_date, 10, "10_days_repoList" + J_EXTENSION)
print("time elapsed: {:.2f}s".format(time.time() - start_time))

# for a in range(100):
#     response = external_request('https://api.github.com/users/phxql/followers')
#     if response.ok:
#         print("Response : " + str(a) + " okay!")
#     else:
#         print(response.text)
# print(api_requests)
#print(response.text)