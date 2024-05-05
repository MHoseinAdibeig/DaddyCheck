import os
import redis
import mimetypes

from ipware import get_client_ip
from datetime import date
from ecdsa import VerifyingKey, BadSignatureError
from celery import chord
from wsgiref.util import FileWrapper

from django.conf import settings
from django.http import HttpResponse
from django.db.models import Q

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser


from .serializers import (
    GadgetSerializer,
    AnalysisSerializer,
    ResultSerializer,
    SampleDetailSerializer,
    StateSerializer,
)
from .models import Gadget, Analysis, State, SampleDetail, Result
from .utils.validation import is_the_input_valid
from .utils.tools import conclude_analysis, video_analyser

from src.core.models import Device
from src.gadget_master.models import DeviceModel
from src.exceptions import MessagedException


class Analyse(APIView):
    """
        Initiate Analysis  
        - Input: POST:{"video1", "video2", "video3"}  
        - Output: POST:{"detail"}  
        -  
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        try:
            analysis = Analysis.objects.get(
                user=request.user, state=State.objects.get(code="waiting_for_vids")
            )
        except Analysis.DoesNotExist:
            raise MessagedException(message="err_analysis_badstate")



class AnalysisBegin(APIView):
    """
        Initialize Analysis  
        - Input: POST:{"title", "serial_number", "viscosity", "color", "volume"}  
        - Output: POST:{"detail"}  
        - 
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        pass


class AnalysisDiscard(APIView):
    """
        Discard Analysis  
        - Input: POST:{}  
        - Output: POST:{"detail"}  
        -    
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        pass


class AnalysisState(APIView):
    """
        Video Quality Check  
        - Input: GET:{}  
        - Output: GET:{"analysis_id", "state"}  
        - Next Step: varied  
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        pass


class VideoQC(APIView):
    """
        Video Quality Check  
        - Input: POST:{"image", "index"}  
        - Output: POST:{"detail"}  
        -  
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        pass


class Gadgets(APIView):
    """
        Gadgets  
        - Input: GET:{}, POST:{serial_number}  
        - Output: GET:{array of gadgets}, POST:{gadget, "detail"}  
        -  
    """

   

    def _gadget_verify(self, user, serial_number):
        signature = bytes.fromhex(serial_number[45:141])
        pass


class Results(APIView):
    """
        Results  
        - Input: GET:{}  
        - Output: GET:{array of completed analyses}
        -   
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        pass


class ResultDetail(APIView):
    """
        Result Detail  
        - Input: GET:{"analysis_id"}  
        - Output: GET:{result details}  
        - 
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        pass



class ResultVideo(APIView):
    """
        Result video  
        - Input: GET:{"analysis_id"}  
        - Output: GET:{result video}
        -
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        pass


class ResultImage(APIView):
    """
        Result image  
        - Input: GET:{"analysis_id"}  
        - Output: GET:{result image}
             
    """

    pass

    def get(self, request):
        pass


class States(APIView):
    """
        States  
        - Input: GET:{}  
        - Output: GET:{states' details}  
        -  
    """
    pass
