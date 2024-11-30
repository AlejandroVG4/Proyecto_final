from django.http import JsonResponse
from .utils.getSasUrl import get_sas_url
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny



# Create your views here.

class GenerateSasUrlView(APIView):

    # TODO Restringir 
    permission_classes = [AllowAny]

    def get(self, request):

        try:
            url = get_sas_url()
            return Response({"url" : url}, status=status.HTTP_200_OK)
           
        except Exception as e:
            print(e)

        