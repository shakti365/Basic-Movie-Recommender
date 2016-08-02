from scipy.spatial.distance import jaccard
import numpy as np
import pandas as pd
import operator
import json
import requests
from sklearn.feature_extraction.text import TfidfVectorizer

url = 'http://10.10.76.125:2000/api/'

genreV = requests.get(url+'movies/genreV/all').json()

        #create dataframe
vec = pd.DataFrame(genreV)
t = TfidfVectorizer()
t.fit(vec['title'])
title_array = t.transform(vec['title']).toarray()
df1 = pd.DataFrame(title_array)
df1 = df1.T
df1.columns = vec['movieId']


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



def recommend_movie(movieID):
    url = 'http://10.10.76.125:2000/api/'
    similar_movie = {}

    for i in df.columns:
         similar_movie[i] = 0.2*(1.0 - jaccard(df[movieID],df[i])) + 1.0*(1.0 - jaccard(df1[movieID],df1[i]))
    
    sorted_similar_movie = dict(sorted(similar_movie.iteritems(), key=operator.itemgetter(1), reverse=True)[:500])
    
    #movie sorted with mean ratings and size
    mean_size = requests.get(url+'movies/mean/all').json()
    ms = pd.DataFrame(mean_size)
    ms_t = ms.T
    ms_t.drop(['movie_id'], axis = 0, inplace=True)
    ms_t.columns = ms['movie_id']

    for i in sorted_similar_movie:
        try:
            sorted_similar_movie[i] += 0.5*(ms_t[i][0] + ms_t[i][1])
        except KeyError, e:
            continue

    sorted_similar_movie = dict(sorted(sorted_similar_movie.iteritems(), key=operator.itemgetter(1), reverse=True)[:12])

    movie_details = {}
    for i in sorted_similar_movie:
        movie_details[i] = i,requests.get(url+'movies/'+str(i)).json()['title']
        print movie_details[i]
        print i
    return json.dumps(movie_details, sort_keys=True)

