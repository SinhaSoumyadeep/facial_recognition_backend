
from rest_framework.views import APIView
from rest_framework.response import Response
import face_recognition
import numpy as np
import json
import os
import errno
from operator import itemgetter
import boto3


celebrity_encodings = []
face_map ={}

session = boto3.session.Session(profile_name='faces')
s3_client = session.client('s3')

def encode_celebrity_faces():
    path = 'images'
    data = []
    for filename in os.listdir(path):
        image = face_recognition.face_encodings(face_recognition.load_image_file(path+"/"+filename))[0]
        image_list = image.tolist()
        img ={}
        img[filename] = image_list
        data.append(img)

    with safe_open_w('encodings/data.json', 'w') as outfile:
        json.dump(data, outfile)


def download_dir(local, bucket, client=s3_client):
    keys = []
    dirs = []
    next_token = ''
    base_kwargs = {
        'Bucket': bucket,

    }
    while next_token is not None:
        kwargs = base_kwargs.copy()
        if next_token != '':
            kwargs.update({'ContinuationToken': next_token})
        results = client.list_objects_v2(**kwargs)
        contents = results.get('Contents')
        for i in contents:
            k = i.get('Key')
            if k[-1] != '/':
                keys.append(k)
            else:
                dirs.append(k)
        next_token = results.get('NextContinuationToken')
    for d in dirs:
        dest_pathname = os.path.join(local, d)
        if not os.path.exists(os.path.dirname(dest_pathname)):
            os.makedirs(os.path.dirname(dest_pathname))
    for k in keys:
        dest_pathname = os.path.join(local, k)
        if not os.path.exists(os.path.dirname(dest_pathname)):
            os.makedirs(os.path.dirname(dest_pathname))

        client.download_file(bucket, k, dest_pathname)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise


def safe_open_w(path, token):
    ''' Open "path" for writing, creating any parent directories as needed.
    '''
    mkdir_p(os.path.dirname(path))
    return open(path, token)


def pre_load():
    download_dir("images", "facial-rec-1992-known-bucket")
    encode_celebrity_faces()


class MyOwnView(APIView):
    def post(self, request):
        data = request.data
        dict1 = data['upload']
        unknown_encoding = np.array(dict1)
        results = face_recognition.face_distance(celebrity_encodings, unknown_encoding)

        m = ''
        dis = min(results)
        if len(results) != 0:
            m = min(enumerate(results), key=itemgetter(1))[0]
            print(face_map.get(m))

        return Response({'url': face_map.get(m), 'distance': dis})

    def get(self, request):
        with safe_open_w('encodings/data.json', 'r') as json_file:
            data = json.load(json_file)

        count = 0
        for items in data:
            key = list(items.keys())[0]
            # print(key)
            face_map[count] = key
            celebrity_encodings.append(items[key])
            count = count + 1

        return Response({'loaded': True})


class MyOtherView(APIView):
    def post(self, request):
        data = request.data
        img = data['image']

        unknown_image = face_recognition.load_image_file(img.open())
        unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
        return Response({'upload': unknown_encoding})





