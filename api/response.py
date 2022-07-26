from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import JsonResponse
from . import serializer
from  . serializer import TrackSerializer
from flask import jsonify, make_response

import sys
import spotipy
import spotipy.util as util
import json


from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

import tensorflow as tf
from keras.models import model_from_json
from keras.preprocessing import image

import io
import base64
import numpy as np
from PIL import Image

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
    getAudioFeatures(sp,res[0])
    
    return Response(res[1])



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
    print(serializer.data)
        

    return topTracksUri,top_tracks_list



def getAudioFeatures(sp,top_tracks_list):
    song_audio_features =[]
    song_data =sp.audio_features(top_tracks_list)



    # for tracks in top_tracks_list:
    #     song_data =sp.audio_features(tracks['uri'])
    #     song_audio_features.append(song_data)
       
    print(song_data)



@app.websocket("ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        # sbuf = StringIO()
        # sbuf.write(data_image)

        # decode and convert into image
        data = await websocket.receive_text()
        data = data.split("$$$$")
        x, y, w, h = [int(x) for x in data[1].split(',')]
        data = data[0]

        b = io.BytesIO(base64.b64decode(data))
        pimg = Image.open(b)

        # # converting RGB to BGR, as opencv standards
        frame = cv2.cvtColor(np.array(pimg), cv2.COLOR_RGBA2GRAY)

        # Process the image frame
        # frame = imutils.resize(frame, width=700)

        # frame = cv2.flip(frame, -1)
        roi_gray = frame[y:y + w, x:x + h]
        roi_gray = cv2.resize(roi_gray, (48, 48))

        img_pixels = tf.keras.utils.img_to_array(roi_gray)
        img_pixels = np.expand_dims(img_pixels, axis=0)
        img_pixels /= 255.0

        predictions = model.predict(img_pixels)
        max_index = int(np.argmax(predictions))

        emotions = ['neutral', 'happiness', 'surprise',
                    'sadness', 'anger', 'disgust', 'fear']
        predicted_emotion = emotions[max_index]

        print(predicted_emotion)

        imgencode = cv2.imencode('.jpg', roi_gray)[1]

        # base64 encode
        stringData = base64.b64encode(imgencode).decode('utf-8')
        b64_src = 'data:image/jpg;base64,'
        stringData = b64_src + stringData

        await websocket.send_text(f"{stringData}")

    


