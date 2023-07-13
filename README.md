# git_stats_app

App is base on FAST API, uvicorn server and TinyDB

1] FAST API Rutine
  Run server:
    uvicorn githubApiRutine:app
  app doc url:  http://127.0.0.1:8000/docs

App contains a three APIs repo, stat, list_repo

API repo - calculates average time between pull requests
  Input: repository name or strig "default"
  Output: dictionary consist of result and intermediate result
  
  For given repository name will be calculate the average time only for pull requests bound to the repository
  For given "default" will be calculate the average time for all pull requests in DB
  
  Reslut value named as "avg" in returned dictionary
  Intermediate result values are "len" - count of pull requests, "sum" - sum of time between pull requests

API stat - calculates count of all event types in defined time offset
  Input: time offest
  Output: dictionary consist of result and intermediate result

  For given time offset produces the valid time interval. In the time interval count all events for defined event types
  The time interval is defined as: time of last inserted record in database - time offset

API list_repo - calculate most often repository names (based on count of pull request)
  Input: none
  Output: list of repository names

  Will count all pull requests in each repository in database and generate a list of repository names with most counts of pull  
  requests

2] FAST API Chart Rutine
  Run server:
    uvicorn githubApiChartRutine:app
  app doc url:  http://127.0.0.1:8000/docs

App contains one root API

root API ('/') - shows simple html with pre-generated image witch github satatistic chart. Image pre-generation is done during startup.
