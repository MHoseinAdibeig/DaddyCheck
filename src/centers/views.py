from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from .serializers import CenterSerializer, CategorySerializer, CitySerializer
from .models import Category, Center, City


class Centers(APIView):
    """
        Centers  
        - Input: GET:{}  
        - Output: GET:{centers' details}  
        - Next Step: varied  
    """

    def get(self, request):
        centers = Center.objects.all()
        serialized = CenterSerializer(centers, many=True)

        return Response(serialized.data, status=status.HTTP_200_OK)


class Categories(APIView):
    """
        Categories  
        - Input: GET:{}  
        - Output: GET:{categories' details}  
        - Next Step: varied  
    """

    def get(self, request):
        categories = Category.objects.all()
        serialized = CategorySerializer(categories, many=True)

        return Response(serialized.data, status=status.HTTP_200_OK)


class Cities(APIView):
    """
        Cities  
        - Input: GET:{}  
        - Output: GET:{cities' details}  
        - Next Step: varied  
    """

    def get(self, request):
        cities = City.objects.all()
        serialized = CitySerializer(cities, many=True)

        return Response(serialized.data, status=status.HTTP_200_OK)
