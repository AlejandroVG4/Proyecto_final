from django.http import JsonResponse
from .utils.getSasUrl import get_sas_url
from .utils.visionAnalysis import analyze_image
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated



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

# Imagen de prueba

class AnalyzeImageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print("En peticion post")
        img_url = request.data.get('img_url')

        if not img_url:
            return Response({"error": "Imagen Requerida"}, status=status.HTTP_400_BAD_REQUEST)

        result = analyze_image(img_url)

        if "error" in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(result, status=status.HTTP_200_OK)

