import io
import secrets
import time

from datetime import datetime
from unittest import skipUnless

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from src.core.serializers import MessageLevelSerializer, MessageSerializer
from src.core.models import Device, Message
from src.analysis.models import Gadget
from src.gadget_master.models import DeviceModel
from src.bucket import Bucket
from src.celery import app

from ..serializers import GadgetSerializer, StateSerializer

_PASSW0RDS = ["passw0rd1"]
_MACS = ["00:1B:44:11:3A:B7"]
_MODELS = ["testmodel1"]
_PLATFORMS = ["testOS1"]
_SERIALS = [
    "001761359fa820cbb18f902d0563182ac5804202101016cdda5610ce5c7658383f7a33fa7d33aa84d33d809349cceaa6d8b70a749b0212977cfedb744f5d25754acec41da5730"
]


# TODO try replace user authentication methods with force_authenticate and self.user
class AnalysisTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Populate Messages table from saved json file if it's unpopulated.
        # TODO It didn't work. had to add `--parallel 2` to `python manage.py test` to fix
        # TODO also, search for "forcing django test run sequentially"

        with open(settings.CDN_LOCAL_DIR + "messagelevels.json", "rb",) as f:
            content = f.read()

        stream = io.BytesIO(content)
        data = JSONParser().parse(stream)
        serialized = MessageLevelSerializer(data=data, many=True)
        serialized.is_valid()
        serialized.save()

        with open(settings.CDN_LOCAL_DIR + "messages.json", "rb") as f:
            content = f.read()

        stream = io.BytesIO(content)
        data = JSONParser().parse(stream)
        serialized = MessageSerializer(data=data, many=True)
        serialized.is_valid()
        serialized.save()

        with open(settings.CDN_LOCAL_DIR + "states.json", "rb") as f:
            content = f.read()

        stream = io.BytesIO(content)
        data = JSONParser().parse(stream)
        serialized = StateSerializer(data=data, many=True)
        serialized.is_valid()
        serialized.save()

        return super().setUpTestData()

    def setUp(self):
        self.startTime = time.time()

    def tearDown(self):
        t = time.time() - self.startTime
        print("%s: %.3f" % (self.id(), t))

    def test_gadgets_get(self):
        user = self._create_user()
        self._activate_user(user)
        token, _created = Token.objects.get_or_create(user=user)

        Gadget.objects.create(
            serial_number=_SERIALS[0],
            remaining_count=4,
            expiration_date=datetime(2021, 1, 1),
            device=Device.objects.get(user=user),
        ).save()
        response = self.client.get(
            reverse("analysis_gadgets"), HTTP_AUTHORIZATION=f"Token {token.key}",
        )
        device = Device.objects.get(user=user, is_active=True)
        gadgets = Gadget.objects.filter(device=device)
        serializer = GadgetSerializer(gadgets, many=True)
        # data = JSONRenderer().render(serializer.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            serializer.data, response.data
        )  # JSONRenderer().render(response.data))

    def test_gadgets_post(self):
        user = self._create_user()
        self._activate_user(user)
        token, _created = Token.objects.get_or_create(user=user)
        DeviceModel.objects.create(id=1, name=_MODELS[0]).save()
        response = self.client.post(
            reverse("analysis_gadgets"),
            HTTP_AUTHORIZATION=f"Token {token.key}",
            data={"serial_number": _SERIALS[0]},
        )
        gadget = Gadget.objects.get(serial_number=_SERIALS[0])
        msg_id = "inf_gadget_added"
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(gadget.id, response.data["id"])
        self.assertEqual(gadget.serial_number, response.data["serial_number"])
        self.assertEqual(gadget.remaining_count, response.data["remaining_count"])
        self.assertEqual(gadget.expiration_date, response.data["expiration_date"])
        self.assertEqual(gadget.device.model, response.data["device__model"])
        self.assertEqual(gadget.device.model, _MODELS[0])
        self.assertEqual(msg_id, response.data["detail"])

    def test_analysis_state_notfound(self):
        user = self._create_user()
        self._activate_user(user)
        token, _created = Token.objects.get_or_create(user=user)
        response = self.client.get(
            reverse("analysis_state"), HTTP_AUTHORIZATION=f"Token {token.key}",
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("notfound", response.data["state"])

    # @skipUnless(
    #     app.conf.task_always_eager, "celery workers can't access test database",
    # )
    def test_analysis_process(self):
        user = self._create_user()
        self._activate_user(user)
        token, _created = Token.objects.get_or_create(user=user)

        # Checking analysis state (NOTE repeated from another test, may seem unnecessary)
        response = self.client.get(
            reverse("analysis_state"), HTTP_AUTHORIZATION=f"Token {token.key}",
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("notfound", response.data["state"])

        # Adding gadget (NOTE repeated from another test, may seem unnecessary)
        DeviceModel.objects.create(id=1, name=_MODELS[0],).save()
        response = self.client.post(
            reverse("analysis_gadgets"),
            HTTP_AUTHORIZATION=f"Token {token.key}",
            data={"serial_number": _SERIALS[0]},
        )
        gadget = Gadget.objects.get(serial_number=_SERIALS[0])
        msg_id = "inf_gadget_added"
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(gadget.id, response.data["id"])
        self.assertEqual(gadget.serial_number, response.data["serial_number"])
        self.assertEqual(gadget.remaining_count, response.data["remaining_count"])
        self.assertEqual(gadget.expiration_date, response.data["expiration_date"])
        self.assertEqual(gadget.device.model, response.data["device__model"])
        self.assertEqual(gadget.device.model, _MODELS[0])
        self.assertEqual(msg_id, response.data["detail"])

        # Beginning new analysis
        response = self.client.post(
            reverse("analysis_create"),
            HTTP_AUTHORIZATION=f"Token {token.key}",
            data={
                "title": "test",
                "serial_number": gadget.serial_number,
                "viscosity": "test",
                "color": "test",
                "volume": "test",
            },
        )
        msg_id = "inf_analysis_initialized"
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(msg_id, response.data["detail"])

        # Check analysis state
        response = self.client.get(
            reverse("analysis_state"), HTTP_AUTHORIZATION=f"Token {token.key}",
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("waiting_for_qc1", response.data["state"])

        # Video QC
        for i in range(1, 4):

            f = File(
                open(
                    settings.PROJECT_ROOT + f"/analysis/tests/samples/qc{i}.jpg", "rb"
                ),
            )
            img_file = SimpleUploadedFile("qc.jpg", f.read(), "image/jpeg")

            response = self.client.post(
                reverse("analysis_qc"),
                HTTP_AUTHORIZATION=f"Token {token.key}",
                data={"index": i, "image": img_file,},
                format="multipart",
            )
            msg_id = "inf_image_accepted"
            self.assertEqual(status.HTTP_200_OK, response.status_code)
            self.assertEqual(msg_id, response.data["detail"])

        # Check analysis state
        response = self.client.get(
            reverse("analysis_state"), HTTP_AUTHORIZATION=f"Token {token.key}",
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("waiting_for_vids", response.data["state"])

        # Run analysis
        vids = []
        for i in range(1, 4):
            f = File(
                open(
                    settings.PROJECT_ROOT + f"/analysis/tests/samples/vid{i}.mp4", "rb"
                ),
            )
            vid_file = SimpleUploadedFile(f"vid{i}.mp4", f.read(), "")
            vids.append(vid_file)

        response = self.client.post(
            reverse("analysis_run"),
            HTTP_AUTHORIZATION=f"Token {token.key}",
            data={
                "video1": vids[0],
                "video2": vids[1],
                "video3": vids[2],
                "sync": True,
            },
            format="multipart",
        )
        msg_id = "inf_analysis_completed"
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(msg_id, response.data["detail"])

        # Check analysis state
        response = self.client.get(
            reverse("analysis_state"), HTTP_AUTHORIZATION=f"Token {token.key}",
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("results_ready", response.data["state"])

        # Retrieve results
        #   Find last analysis id
        response = self.client.get(
            reverse("analysis_results"), HTTP_AUTHORIZATION=f"Token {token.key}",
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        last_analysis_id = next(
            analysis["analysis"]["id"]
            for analysis in sorted(
                response.data, key=lambda x: x["analysis"]["register_date"]
            )
        )

        #   Retrieve the details of that analysis
        response = self.client.get(
            reverse("analysis_detail"),
            HTTP_AUTHORIZATION=f"Token {token.key}",
            data={"analysis_id": last_analysis_id},
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        #   Retrieve the video of that analysis
        response = self.client.get(
            reverse("analysis_video"),
            HTTP_AUTHORIZATION=f"Token {token.key}",
            data={"analysis_id": last_analysis_id},
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        #   Retrieve the image of that analysis
        response = self.client.get(
            reverse("analysis_image"),
            HTTP_AUTHORIZATION=f"Token {token.key}",
            data={"analysis_id": last_analysis_id},
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def _create_user(self):

        email = "user@example.com"
        password = _PASSW0RDS[0]
        mac = _MACS[0]
        model = _MODELS[0]
        platform = _PLATFORMS[0]

        user = get_user_model().objects.create_user(
            email=email, password=password, confirm_code=secrets.randbits(16)
        )
        device = Device.objects.create(
            mac=mac, model=model, platform=platform, user=user,
        )
        user.save()
        device.save()
        return user

    def _activate_user(self, user):
        user.is_active = True
        user.save()

    # def _add_gadget_for_user(self, user, serial_number, device_model):
    #     # NOTE this method uses indirect adding of data to the database
    #     #   by using the corresponding view and making a request to it.
    #     #   An alternative method would be using ORM to create the instance.

    #     token, _created = Token.objects.get_or_create(user=user)
    #     DeviceModel.objects.create(id=1, name=device_model,).save()
    #     self.client.post(
    #         reverse("analysis_gadgets"),
    #         HTTP_AUTHORIZATION=f"Token {token.key}",
    #         data={"serial_number": serial_number},
    #     )
