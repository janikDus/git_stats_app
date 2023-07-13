# main.py

# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring

from datetime import datetime
from datetime import timedelta
import requests
import time
from collections import Counter
import random

from tinydb import TinyDB, Query
from fastapi import FastAPI
from pydantic import BaseModel


GIT_EVENTS_URL = 'https://api.github.com/events'
VAILD_EVENT_TYPES = {'WatchEvent', 'PullRequestEvent', 'IssuesEvent'}
MAX_EVENT_IN_DB = 900
MAX_COMMON_REPOS = 10
DEFAULT_REPO_NAME = 'default'


class Repo(BaseModel):
    repository_name: str


class Stat(BaseModel):
    offset: int


app = FastAPI()


@app.post("/repo/")
async def create_item(repo: Repo):
    '''
    Page repo calculate average time between pull requests
    Input: repository name or strig "default"
    Output: dictionary consist of result and intermediate result
    '''
    response = {}
    if repo.repository_name:
        response['repository_name'] = '{}'.format(repo.repository_name)

        db = TinyDB('./github_api_db.json')
        event = Query()

        if repo.repository_name == DEFAULT_REPO_NAME:
            pulls = db.search(event.type == 'PullRequestEvent')
        else:
            pulls = db.search((event.type == 'PullRequestEvent') & (event.repo_name == repo.repository_name))

        pull_times = []
        for pull in pulls:
            pull_times.append(datetime.strptime(pull['created_at'], "%Y-%m-%dT%H:%M:%SZ"))
        pulls_time_line = sorted(pull_times)

        sum_delta = 0
        for index in range(0, len(pulls_time_line) - 1):
            delta = pulls_time_line[index + 1] - pulls_time_line[index]
            sum_delta += delta.seconds
        delta_avg = sum_delta / (len(pulls_time_line) - 1)

        response['len'] = len(pulls_time_line)
        response['sum'] = sum_delta
        response['avg'] = delta_avg

        db.close()

    return response


@app.post("/stat/")
async def create_item(stat: Stat):
    '''
    Page stat calculate counts of all event types in defined time offset
    Input: time offest
    Output: dictionary consist of result and intermediate result
    '''
    response = {}
    if stat.offset:
        response['offset'] = '{}'.format(stat.offset)

        db = TinyDB('./github_api_db.json')
        event = Query()

        last_record = db.all()[-1]
        last_insertion = datetime.strptime(last_record['inserted_at'], "%Y-%m-%d %H:%M:%S")

        date_offset = last_insertion - timedelta(minutes=stat.offset)
        date_trigger = date_offset.strftime("%Y-%m-%d %H:%M:%S")

        collected_data = db.search(event.inserted_at > date_trigger)
        response['all_data_count'] = len(collected_data)

        event_types = []
        for event in collected_data:
            event_types.append(event['type'])

        event_stats = Counter(event_types)
        response['event_stats'] = event_stats

        db.close()

    return response


@app.post("/list_repo/")
async def create_item():
    '''
    Page list_repo calculate most often repository names (based on count of pull request)
    Input: none
    Output: list of repository names
    '''
    response = {}
    db = TinyDB('./github_api_db.json')
    event = Query()

    pulls = db.search(event.type == 'PullRequestEvent')
    pull_repo_names = []
    for pull in pulls:
        pull_repo_names.append(pull['repo_name'])

    repo_name_stats = Counter(pull_repo_names)
    response['repo_name_stats'] = repo_name_stats.most_common(MAX_COMMON_REPOS)

    db.close()

    return response


@app.on_event("startup")
async def startup():
    '''
    On event startup populate the database
    '''
    db = TinyDB('./github_api_db.json')
    event = Query()
    collected_data = len(db.all())
    print('collected_data: {}'.format(collected_data))

    while collected_data < MAX_EVENT_IN_DB:

        git_response = requests.get(GIT_EVENTS_URL)
        print('collected_data: {}'.format(collected_data))

        if git_response.status_code == 200:

            git_events = git_response.json()

            for git_event in git_events:

                if git_event['type'] in VAILD_EVENT_TYPES:
                    event_data = {
                        'id': git_event['id'],
                        'type': git_event['type'],
                        'repo_id': git_event['repo']['id'],
                        'repo_name': git_event['repo']['name'],
                        'created_at': git_event['created_at'],
                        'inserted_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }

                    result = db.search(event.id == git_event['id'])
                    if not result:
                        db.insert(event_data)

            collected_data = len(db.all())

            time.sleep(random.randint(10, 20))
        else:
            time.sleep(300)

    db.close()
