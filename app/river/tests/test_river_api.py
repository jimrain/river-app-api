"""
Test for rvier APIs
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import River
from rest_framework.utils import json

from river.serializers import (
    RiverSerializer,
    RiverDetailSerializer,
)

RIVERS_URL = reverse('river:river-list')


def detail_url(river_id):
    """Create and return a recipe detail URL."""
    return reverse('river:river-detail', args=[river_id])


def create_river(user, **params):
    """Create and return a sample river"""
    defaults = {
        'name': 'Rogue River',
        'feature': 'Stream',
        'state': 'OR',
        'miles': 47.3,
        'region': 1,
        'geometry_type': 'LineString',
        'coordinates': [
            [-159.55596127142, 63.8967914977418],
            [-159.55629960491, 63.8952464976259],
            [-159.557151821688, 63.8904670545064],
        ]
    }
    defaults.update(params)

    river = River.objects.create(user=user, **defaults)
    return river


class PublicRiverAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required"""
        res = self.client.get(RIVERS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRiverApiTests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_river(self):
        """test_retrieving a list of rivers."""
        create_river(user=self.user)
        create_river(user=self.user)

        res = self.client.get(RIVERS_URL)

        rivers = River.objects.all().order_by('-id')
        serializer = RiverSerializer(rivers, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user."""
        other_user = get_user_model().objects.create_user(
            'other.example.com',
            'password123',
        )
        create_river(user=other_user)
        create_river(user=self.user)
        res = self.client.get(RIVERS_URL)

        rivers = River.objects.filter(user=self.user)
        serializer = RiverSerializer(rivers, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_river_detail(self):
        """Test get river detail."""
        river = create_river(user=self.user)

        url = detail_url(river.id)
        res = self.client.get(url)

        serializer = RiverDetailSerializer(river)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_river(self):
        """Test creating a recipe"""
        coordinates = []
        coordinates.append([-159.55596127142, 63.8967914977418])
        payload = {
            "name": 'Test River',
            "feature": 'Stream',
            "state": 'OR',
            "region": 1,
            "miles": 47.3,
            "geometry_type": 'LineString',
            "coordinates": coordinates,
        }
        res = self.client.post(RIVERS_URL, json.dumps(payload),
                               content_type='application/json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        river = River.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(river, k), v)
        self.assertEqual(river.user, self.user)
