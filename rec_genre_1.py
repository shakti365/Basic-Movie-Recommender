from flask import Flask
from flask.ext.cors import CORS 
import numpy as np
import flask
import pandas as pd
import requests
from scipy.spatial.distance import jaccard
import requests
import operator
import json



app = Flask(__name__)
CORS(app)
url = 'http://10.10.76.125:2000/api/'

@app.route('/recomend/<movieID>')
def reccomend(movieID):

	movieID = int(movieID)
	#requests genre
	genreV = requests.get(url+'movies/genreV/all').json()

	#create dataframe
	vec = pd.DataFrame(genreV)

	#create genre vector
	vec['genresV'] = vec['genresV'].str.split('|')

	list_movieid = list(vec['movieId'])

	v = vec.T
	v.columns = list_movieid

	v.drop(['movieId'], inplace=True)

	v_json = v.to_dict(orient='records')
	#v_json = v.to_dict(orient='series')
	#d = requests.post('http://10.10.76.125:1000/api/movies', v_json)

	#v_res = d.json()

	df = pd.DataFrame.from_dict(v_json[0], orient='index')
	
	df.drop([20], axis = 1, inplace=True)
	
	df = df.T
	
	df = df.astype(int)
	
	similar_movie = {}

	for i in df.columns:
	     similar_movie[i] = 1.0 - jaccard(df[movieID],df[i])
	
	sorted_similar_movie = dict(sorted(similar_movie.iteritems(), key=operator.itemgetter(1), reverse=True)[:500])
	
	#movie sorted with mean ratings and size
	mean_size = requests.get(url+'movies/mean/all').json()
	ms = pd.DataFrame(mean_size)
	ms_t = ms.T
	ms_t.drop(['movie_id'], axis = 0, inplace=True)
	ms_t.columns = ms['movie_id']

	for i in sorted_similar_movie:
		try:
			sorted_similar_movie[i] += ms_t[i][0] + ms_t[i][1]
		except KeyError, e:
			continue

	sorted_similar_movie = dict(sorted(sorted_similar_movie.iteritems(), key=operator.itemgetter(1), reverse=True)[:12])
	print sorted_similar_movie

	movie_details = {}
	for i in sorted_similar_movie:
	    movie_details[i] = i,requests.get(url+'movies/'+str(i)).json()['title']
	    print movie_details[i]
	    print i
	return json.dumps(movie_details, sort_keys=True)



@app.route('/')
def test():
	return 'working'

if __name__=="__main__":
	app.run(host='192.168.0.101',debug=True)
