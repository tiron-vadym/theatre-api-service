import tempfile
import os
from datetime import datetime

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from theatre.models import Play, Actor, Genre, TheatreHall, Performance
from theatre.serializers import PlayDetailSerializer, PlayListSerializer

PLAY_URL = reverse("theatre:play-list")
PERFORMANCE_URL = reverse("theatre:performance-list")


def sample_actor(**params):
    defaults = {"first_name": "George", "last_name": "Clooney"}
    defaults.update(params)

    return Actor.objects.create(**defaults)


def sample_genre(**params):
    defaults = {
        "name": "Drama",
    }
    defaults.update(params)

    return Genre.objects.create(**defaults)


def sample_play(**params):
    defaults = {
        "title": "Sample play",
        "description": "Sample description",
        "actors": sample_actor(),
        "genres": sample_genre(),
        "image": "sample_image.jpg",
    }
    defaults.update(params)

    return Play.objects.create(**defaults)


def sample_performance(**params):
    theatre_hall = TheatreHall.objects.create(
        name="Sample theatre",
        rows=10,
        seats_in_row=20
    )
    defaults = {
        "play": sample_play(),
        "theatre_hall": theatre_hall,
        "show_time": datetime.now(),
    }
    defaults.update(params)

    return Performance.objects.create(**defaults)


def image_upload_url(play_id):
    """Return URL for recipe image upload"""
    return reverse("theatre:play-upload-image", args=[play_id])


def detail_url(play_id):
    return reverse("theatre:play-detail", args=[play_id])


class PlayImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@myproject.com", "password"
        )
        self.client.force_authenticate(self.user)
        self.actor = sample_actor()
        self.genre = sample_genre()
        self.play = sample_play()
        self.performance = sample_performance()

    def tearDown(self):
        self.play.image.delete()

    def test_upload_image_to_play(self):
        """Test uploading an image to play"""
        url = image_upload_url(self.play.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.play.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.play.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.play.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_play_list(self):
        url = PLAY_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "title": "Title",
                    "description": "Description",
                    "duration": 90,
                    "actors": [1],
                    "genres": [1],
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        play = Play.objects.get(title="Title")
        self.assertFalse(play.image)

    def test_image_url_is_shown_on_play_detail(self):
        url = image_upload_url(self.play.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(detail_url(self.play.id))

        self.assertIn("image", res.data)

    def test_image_url_is_shown_on_play_list(self):
        url = image_upload_url(self.play.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(PLAY_URL)

        self.assertIn("image", res.data[0].keys())

    def test_image_url_is_shown_on_performance_detail(self):
        url = image_upload_url(self.play.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(PERFORMANCE_URL)

        self.assertIn("play_image", res.data[0].keys())


class UnAuthenticatedUserToPlay(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_trying_to_get_any_information(self):
        res = self.client.get(reverse("theatre:play-list"))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        res = self.client.get(reverse("theatre:play-detail", args=["1"]))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


def create_play(data):
    return Play.objects.create(**data)


class AuthenticatedUserToPlay(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@gmail.com",
            password="test123",
        )
        self.client.force_authenticate(self.user)

    def test_list_view(self):
        genre = Genre.objects.create(name="play")
        play1 = {
            "title": "Test1",
            "duration": "2",
        }
        play2 = {
            "title": "Test2",
            "duration": "2",
        }
        play1 = create_play(play1)
        play2 = create_play(play2)
        play1.genres.set([genre])
        play2.genres.set([genre])
        res = self.client.get(reverse("theatre:play-list"))
        serializer = PlayListSerializer([play1, play2], many=True)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_play(self):
        genre = Genre.objects.create(name="play")
        play1 = {
            "title": "Test1",
            "duration": "2",
        }
        play1 = create_play(play1)
        play1.genres.set([genre])
        res = self.client.get(reverse("theatre:play-detail", args=["1"]))
        serializer = PlayDetailSerializer(play1)
        self.assertEqual(res.data, serializer.data)

    def test_create_play(self):

        res = self.client.post(reverse("theatre:play-list"), {
            "title": "Test1",
            "duration": "2",
        })
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserToPlay(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@gmail.com",
            "test123",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_play(self):
        Genre.objects.create(name="play")
        Actor.objects.create(first_name="leo", last_name="ant")
        payload = {
            "title": "Test1",
            "description": "ad",
            "duration": "2",
            "genres": [1, ],
            "actors": [1, ]
        }
        res = self.client.post(reverse("theatre:play-list"), payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(Play.objects.all()), 1)
        self.assertEqual(Play.objects.get(id=1).title, "Test1")
