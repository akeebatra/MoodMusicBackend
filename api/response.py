from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import JsonResponse
from . import serializer
from  . serializer import TrackSerializer
from flask import jsonify, make_response
from sklearn.preprocessing import StandardScaler

import sys
import spotipy
import spotipy.util as util
import json

import math

import pandas as pd


from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

import tensorflow as tf
from keras.models import model_from_json
from keras.preprocessing import image
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasClassifier
from keras.utils import np_utils
from keras.models import Sequential


import io
import base64
import numpy as np
from PIL import Image
import pickle


client_id = "acca5513fecb49e7bb8fcb5f886b04b7"
client_secret = "782cd7c2bc674b68bbd57bdc19e28265"
redirect_uri = "http://localhost:3000"
scope = "streaming%20user-read-email%20user-read-private%20user-library-read%20user-top-read%20playlist-modify-public%20user-follow-read%20user-library-modify%20user-read-playback-state%20user-modify-playback-state"
username = ""


app = FastAPI()

json_file = open('/Users/akshay/Desktop/Django/Backend/api/ML/fer.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
model = model_from_json(loaded_model_json)
# Load weights and them to model
model.load_weights('/Users/akshay/Desktop/Django/Backend/api/ML/fer.h5')


spotify_features = ['energy', 'liveness', 'tempo', 'speechiness',
                                        'acousticness', 'instrumentalness', 'danceability',
                                        'loudness', 'valence']

user_classified_songs = []

@api_view(['POST'])
def getAuth(request):
    code = request.data.get('code')

    token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)
    sp = spotipy.Spotify(auth=token)

    return JsonResponse({'accessToken':token,'refreshToken':'','expiresIn':''})


@api_view(['POST'])
def get_songs(request):
    token = request.data.get('accessToken')
    sp = spotipy.Spotify(auth=token)

    topArtistUri = getArtists(sp)
    res = getTopTracks(sp,topArtistUri)
    df = getAudioFeatures(res[0],sp)
    
    return Response(classify_songs(df,res[1]))



def getArtists(sp):
    print("Fetching artists...")
    topArtistNames  = []
    topArtistsUri =[]
    range = ['short_term','medium_term','long_term']
    for r in range:
        top_artists_all_data = sp.current_user_top_artists(limit=50, time_range= r)
        top_artists_data = top_artists_all_data['items']
        for artist_data in top_artists_data:
            if artist_data["name"] not in topArtistNames:	
                topArtistNames.append(artist_data['name'])
                topArtistsUri.append(artist_data['uri'])

    followed_artists_all_data = sp.current_user_followed_artists(limit=50)
    followed_artists_data = (followed_artists_all_data['artists'])
    for artist_data in followed_artists_data["items"]:
        if artist_data["name"] not in topArtistNames:
            topArtistNames.append(artist_data['name'])
            topArtistsUri.append(artist_data['uri'])


    return topArtistsUri

def getTopTracks(sp,topArtistsUri):
    topTracksUri = []
    top_tracks_list = []
    for uri in topArtistsUri:
        top_track_response = sp.artist_top_tracks(uri)
        top_tracks = top_track_response['tracks']
        top_tracks_list = top_tracks_list +  top_tracks
        for t in top_tracks:
            topTracksUri.append(t['uri'])
        

    t = top_tracks_list[0]
    serializer = TrackSerializer(t)
    #print(serializer.data)
        

    return topTracksUri,top_tracks_list

def getAudioFeatures(list_uri_or_ids,sp):
    
    song_audio_features =[]
    song_data =sp.audio_features(list_uri_or_ids)


    features_required = ['id', 'energy', 'liveness', 'tempo', 'speechiness',
                                     'acousticness', 'instrumentalness', 'danceability', 'duration_ms',
                                     'loudness', 'valence','uri',]

    
    song_features_df = pd.DataFrame(song_data).drop(['analysis_url', 'key', 'mode', 'time_signature','track_href', 'type'], axis=1)
   
   

   # song_features_df = song_features_df[features_required]
    return song_features_df


    # for tracks in top_tracks_list:
    #     song_data =sp.audio_features(tracks['uri'])
    #     song_audio_features.append(song_data)
 


def classify_songs(song_features_df,res):
    pkl_filename = '/Users/akshay/Desktop/Django/Backend/api/ML/pickle_model_logreg.pkl'
    with open(pkl_filename,'rb') as file:
        pickle_model = pickle.load(file)
    
    scaler = StandardScaler()
    scaled_song_features = scaler.fit_transform(song_features_df[spotify_features])
    pred = pickle_model.predict(scaled_song_features)
    song_features_df['mood'] = pred
    print('len song_features_df', len(song_features_df))
    dic = song_features_df.to_dict('records')

    arr = []
    for item in dic:
        arr.append({'id': item['id'],'mood': item['mood']})
        
    for i in res:
        for a in arr:
            if a['id'] == i['id']:
                i['mood'] = a['mood']


    return res
   
    
        


    
    



@api_view(['POST'])
def suggest_next_song(request):
    user_mood = 'Sad'
    print(user_classified_songs)
    return Response({'a':'b'})





@api_view(['POST'])
def get_playlists(request):
    access_token = request.data.get('access_token')
    sp = spotipy.Spotify(auth=access_token)
    
    playlists = {
             'Relaxing':    ["https://open.spotify.com/playlist/1r4hnyOWexSvylLokn2hUa?si=a622dcb83906450f",
                             "https://open.spotify.com/playlist/11IcIUefRdjIpy1K5GMdOH?si=83b430249c854434",],
            'Aggressive':  ["https://open.spotify.com/playlist/0y1bZzglw6D3t5lPXRmuYS?si=57c0db5e01b9420b",
                             "https://open.spotify.com/playlist/7rthAUYUFcbEeC8NS8Wh42?si=ab7f353f5f2847b3",],
            'Happy' :      ["https://open.spotify.com/playlist/1h90L3LP8kAJ7KGjCV2Xfd?si=5e2691af69e544a3",
                             "https://open.spotify.com/playlist/4AnAUkQNrLKlJCInZGSXRO?si=9846e647548d4026",]}

    tracks = pd.DataFrame()
    moods = []
    
    for mood, links in playlists.items():
        for link in links:
            id = link[34:56]
            try:
                 pl_tracks = sp.playlist_tracks(id)['items']
                 ids = [foo['track']['id'] for foo in pl_tracks]
                
            except:
                print (link)
                continue
            print('len',len(ids))
           # features = get_track_features(ids, sp)
            features = getAudioFeatures(ids,sp)
            #features['id2'] = ids
            features['mood'] = mood
            tracks = tracks.append(features)
            
    
    tracks.to_csv('dataset1.csv')
    return ("")

def get_track_features(track_ids, spotify):




    features_required = [ 'energy', 'liveness', 'tempo', 'speechiness',
                                     'acousticness', 'instrumentalness', 'danceability', 'duration_ms',
                                     'loudness', 'valence','uri',]
   
    chunk_size = 50

    num_chunks = int(math.ceil(len(track_ids) / float(chunk_size)))
    features_add = []
    for i in range(num_chunks):
        chunk_track_ids = track_ids[i * chunk_size:min((i + 1) * chunk_size, len(track_ids))]
        chunk_features = spotify.audio_features(tracks=chunk_track_ids)
        features_add.extend(chunk_features)

    features_df = pd.DataFrame(features_add).drop(['analysis_url', 'key', 'mode', 'time_signature',
                                                   'track_href', 'type'], axis=1)

   

    features_df = features_df[features_required]
    return features_df