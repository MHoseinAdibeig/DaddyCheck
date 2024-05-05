import io
import uuid
import secrets

from datetime import datetime, timezone, timedelta

from django.contrib.auth.hashers import check_password, make_password
from django.conf import settings

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .serializers import MessageSerializer, MessageLevelSerializer, KeySerializer
from .models import User, Device, Message, MessageLevel, Key
from .validators import cleaned_email_to_insert, is_valid_password, is_valid_devicemodel

from src.exceptions import MessagedException
from src.bucket import Bucket


class Signup(APIView):
    """
        User Signup  
        - Input: POST:{"email", "password", "mac", "model", "platform"}  
        - Output: POST:{user details, "detail"}  
        - Next step: /Auth/signup/confirm/  
    """

    def post(self, request):
        pass


class SignupConfirm(APIView):
    """
        Confirm Email  
        - Input: POST:{"user_id", "confirm_code"}  
        - Output: POST:{"detail"}  
        - Next Step: Auth/login/  
    """

    def post(self, request):
        pass


class SignupAnonymous(APIView):
    """
        Anonymous User Signup  
        - Input: POST:{"mac", "model", "platform"}  
        - Output: POST:{user's details, "token", "detail"}  
        - Next step: varied  
    """

    def post(self, request):
        pass


class Login(APIView):
    """
        User Login
        - Input: POST:{"email", "password", "mac", "model", "platform"}  
        - Output: POST:{device details, "token", "detail"}  
        - Next Step: varied  
    """

    def post(self, request):
        pass


class Logout(APIView):
    """
        User Logout  
        - Input: POST:{}  
        - Output: POST:{"detail"}  
        - Next Step: varied  
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        pass


class Profile(APIView):
    """
        User profile  
        - Input: GET:{}, PUT:{"email", "first_name", "last_name", "birth_date", "phone"}  
        - Output: GET:{user's profile}, PUT:{user's profile, "detail"}  
        - Next Step: varied  
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        pass

    def put(self, request):
        pass


class PasswordChange(APIView):
    """
        Change User's Password  
        - Input: POST:{"password", "new_password"}  
        - Output: POST:{"detail"}  
        - Next Step: varied  
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        pass


class PasswordResetRequest(APIView):
    """
        Request a Password Reset
        - Input: POST:{"email"}  
        - Output: POST:{"detail"}  
        - Next Step: /Auth/password/reset/confirm/  
    """

    # NOTE: User's "confirm_code" field has been used for password
    #   reset's code. This choice makes a few flaws in the system but
    #   is more space efficient
    #   Flaw:
    #   1- A user who has recently reset his password can use the same
    #       reset code to bypass password_reset_request and use it directly
    #       in password_reset_confirm API and reset the password again
    #       POSSIBLE ABUSE: Not registering the password request date in the
    #                       database and reset the password many times until
    #                       the code expires
    def post(self, request):
        pass


class PasswordResetConfirm(APIView):
    """
        Confirm a Password Reset Request and Change Password  
        - Input: POST:{"email", "confirm_code", "new_password"}  
        - Output: POST:{"detail"}  
        - Next Step: /Auth/login/  
    """

    def post(self, request):
        pass


class Messages(APIView):
    """
        Messages  
        - Input: GET:{}  
        - Output: GET:{messages' details}  
        - Next Step: varied  
    """

    def get(self, request):
        messages = Message.objects.all()
        serialized = MessageSerializer(messages, many=True)

        return Response(serialized.data, status=status.HTTP_200_OK)


class MessageLevels(APIView):
    """
        Message Levels  
        - Input: GET:{}  
        - Output: GET:{message levels' details}  
        - Next Step: varied  
    """

    def get(self, request):
        messagelevels = MessageLevel.objects.all()
        serialized = MessageLevelSerializer(messagelevels, many=True)

        return Response(serialized.data, status=status.HTTP_200_OK)


class Keys(APIView):
    """
        Keys
        - Input: GET:{}  
        - Output: GET:{message levels' details}  
        - Next Step: varied  
    """

    def get(self, request):
        keys = Key.objects.all()
        serialized = KeySerializer(keys, many=True)

        return Response(serialized.data, status=status.http_200_ok)


class Version(APIView):
    """
        Get Version of CDN  
        - Input: GET:{}  
        - Output: GET:{"version"}
        - Next Step: varied
    """

    def get(self, request):
        with open(Bucket().local_dir + "version.json", "rb",) as f:
            content = f.read()

        stream = io.BytesIO(content)
        data = JSONParser().parse(stream)

        return Response(data, status=status.HTTP_200_OK)
