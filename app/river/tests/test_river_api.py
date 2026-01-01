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


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


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
        self.user = create_user(email='user@example.com', password='test123')
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
        other_user = create_user(email='other.example.com', password='test123')

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

    def test_partial_update(self):
        """Test partial update of a river."""
        coordinates = [[-159.55596127142, 63.8967914977418]]
        river = create_river(user=self.user,
                             name='Owyhee',
                             coordinates=coordinates)

        payload = {'name': 'Deschutes'}
        url = detail_url(river.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        river.refresh_from_db()
        self.assertEqual(river.name, payload['name'])
        self.assertEqual(river.coordinates, coordinates)
        self.assertEqual(river.user, self.user)

    def test_full_update(self):
        """Test full update of river"""
        river = create_river(
            user=self.user,
            feature='Stream',
            state='OR',
            region=1,
            miles=47.3,
            geometry_type='LineString',
            name='Owyhee',
            coordinates=[[-159.55596127142, 63.8967914977418]],
        )

        payload = {
            'name': 'Test River',
            'feature': 'Stream',
            'state': 'CA',
            "region": 2,
            "miles": 43.7,
            "geometry_type": 'Point',
            "coordinates": [[-157.55596127142, 63.8967914977418]],
        }
        url = detail_url(river.id)
        res = self.client.put(url, json.dumps(payload),
                              content_type='application/json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        river.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(river, k), v)
        self.assertEqual(river.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the river user results in an error."""
        new_user = create_user(email='user2@example.com', password='test123')
        river = create_river(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(river.id)
        self.client.patch(url, payload)

        river.refresh_from_db()
        self.assertEqual(river.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe succesful."""
        river = create_river(user=self.user)

        url = detail_url(river.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(River.objects.filter(id=river.id).exists())

    def test_recipe_other_users_recipe_error(self):
        """Test trying to delet another users recipe gives. error."""
        new_user = create_user(email='user2@example.com', password='test123')
        river = create_river(user=new_user)

        url = detail_url(river.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(River.objects.filter(id=river.id).exists())
