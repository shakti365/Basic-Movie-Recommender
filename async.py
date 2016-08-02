from flask import Flask
from flask.ext.cors import CORS 
import numpy as np
import flask
import pandas as pd
import requests
import operator
import json
from sklearn.feature_extraction.text import TfidfVectorizer
#import settings
import async_reco
from rq import Queue
from rq.job import Job
from worker import conn


app = Flask(__name__)
CORS(app)
app.config['RQ_OTHER_HOST'] = 'localhost'
app.config['RQ_OTHER_PORT'] = 6379
app.config['RQ_OTHER_PASSWORD'] = None
app.config['RQ_OTHER_DB'] = 0

q = Queue(connection=conn)


#settings.init()

@app.route('/recomend/<movieID>')
def reccomend(movieID):
    print movieID
    movieID = int(movieID)
    job = q.enqueue(async_reco.recommend_movie, movieID)
    print job.get_id()
    job = Job.fetch(job.get_id(), connection=conn)
    while(job.is_finished==False):
        continue
    return str(job.result), 200
    
@app.route("/results/<job_key>")
def get_results(job_key):

    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        return str(job.result), 200
    else:
        return "Nay!", 202

@app.route('/')
def test():
    return 'working'

if __name__=="__main__":
    app.run(host='192.168.0.101',debug=True)
