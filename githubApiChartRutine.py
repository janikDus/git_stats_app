# main.py

# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from github import Github
import matplotlib.pyplot as plt
from collections import Counter


VAILD_EVENT_TYPES = {'WatchEvent', 'PullRequestEvent', 'IssuesEvent'}


app = FastAPI()

app.mount("/imgs", StaticFiles(directory="imgs"), name='images')


@app.get("/", response_class=HTMLResponse)
def serve():
    return """
    <html>
        <head>
            <title></title>
        </head>
        <body>
        <h1> GitHub Event Statistic </h1>
        <img src="imgs/data.png">
        </body>
    </html>
    """


@app.on_event("startup")
async def startup():
    '''
    On event startup generate and safe the chart
    '''
    api_token = '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'
    git_api = Github(login_or_token=api_token, per_page=100)

    events = git_api.get_events()
    event_types = []
    for event in events:
        if event.type in VAILD_EVENT_TYPES:
            event_types.append(event.type)

    event_stats = Counter(event_types)

    plt.bar(event_stats.keys(), event_stats.values())
    plt.savefig('./imgs/data.png')
