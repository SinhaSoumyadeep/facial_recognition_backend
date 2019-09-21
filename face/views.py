
from rest_framework.views import APIView
from rest_framework.response import Response
import face_recognition
import numpy as np
import json


def test(encoding1, encoding2):

    res = face_recognition.face_distance([encoding1], encoding2)
    results = face_recognition.compare_faces([encoding1], encoding2, 0.57)

    return res, results

# Create your views here.


class MyOwnView(APIView):
    def post(self, request):
        data = request.data
        dict1 = json.loads(data['l'])
        dict2 = json.loads(data['r'])

        c = np.array(dict1)
        d = np.array(dict2)

       # print(c)


        dist, is_match = test(c, d)
        return Response({'distance': dist, 'is_match': is_match})



