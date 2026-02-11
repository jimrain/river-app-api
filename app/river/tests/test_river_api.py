"""
Test for rvier APIs
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.gis.geos import LineString, GEOSGeometry
from core.models import River
from rest_framework.utils import json

from river.serializers import (
    # RiverSerializer,
    RiverDetailSerializer,
)


RIVERS_URL = reverse('river:river-list')


def detail_url(river_id):
    """Create and return a river detail URL."""
    return reverse('river:river-detail', args=[river_id])


def create_river(owner, **params):
    """Create and return a sample river"""

    coordinates = [
        (-159.55596127142, 63.8967914977418),
        (-159.55629960491, 63.8952464976259),
        (-159.557151821688, 63.8904670545064),
    ]
    lineString = LineString(coordinates, srid=4326)
    defaults = {
        'name': 'Rogue River',
        'feature': 'Stream',
        'state': 'OR',
        'miles': 47.3,
        'region': 1,
        'geometry': lineString
        }

    defaults.update(params)

    river = River.objects.create(owner=owner, **defaults)
    return river


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicRiverAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_list_rivers(self):
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
        create_river(owner=self.user)
        create_river(owner=self.user)

        res = self.client.get(RIVERS_URL)

        # rivers = River.objects.all().order_by('-id')
        # serializer = RiverSerializer(rivers, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # This breaks because of pagination - need to figure that out.
        # self.assertEqual(res.data, serializer.data)

    def test_river_list_not_limited_to_user(self):
        """Test list of river is limited to authenticated user."""
        other_user = create_user(email='other.example.com', password='test123')

        create_river(owner=other_user)
        create_river(owner=self.user)
        res = self.client.get(RIVERS_URL)

        # rivers = River.objects.filter(owner=self.user)
        # serializer = RiverSerializer(rivers, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # JMR - rivist this test.
        # self.assertEqual(res.data, serializer.data)

    def test_get_river_detail(self):
        """Test get river detail."""
        river = create_river(owner=self.user)

        url = detail_url(river.id)
        res = self.client.get(url)

        serializer = RiverDetailSerializer(river)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_river(self):
        """Test creating a river"""
        # coordinates = []
        # coordinates.append([-159.55596127142, 63.8967914977418])
        payload = {
            "name": 'Test River',
            "feature": 'Stream',
            "state": 'OR',
            "region": 1,
            "miles": 47.3,
            "geometry": {
                'type': 'LineString',
                'coordinates': [
                    [-159.55596127142, 63.8967914977418],
                    [-159.55629960491, 63.8952464976259],
                    [-159.557151821688, 63.8904670545064],
                ]
            }
        }
        res = self.client.post(RIVERS_URL, json.dumps(payload),
                               content_type='application/json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        river = River.objects.get(id=res.data['id'])
        for k, v in payload.items():
            if k != 'geometry':
                self.assertEqual(getattr(river, k), v)
            else:
                geom_from_json = GEOSGeometry(json.dumps(v))
                db_geo = getattr(river, k)
                assert (db_geo.equals(geom_from_json))
        self.assertEqual(river.owner, self.user)


def test_create_river_multiline(self):
    """Test creating a river"""
    # coordinates = []
    # coordinates.append([-159.55596127142, 63.8967914977418])
    payload = {
        "name": 'Test River',
        "feature": 'Stream',
        "state": 'OR',
        "region": 1,
        "miles": 47.3,
        "geometry": {
            'type': 'MultiLineString',
            'coordinates': [
                [
                    [-159.55596127142, 63.8967914977418],
                    [-159.55629960491, 63.8952464976259],
                    [-159.557151821688, 63.8904670545064],
                ],
                [
                    [-159.55598127142, 63.8967914977418],
                    [-159.55628960491, 63.8952464976259],
                    [-159.557181821688, 63.8904670545064],
                ],
            ]
        }
    }
    res = self.client.post(RIVERS_URL, json.dumps(payload),
                           content_type='application/json')

    self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    river = River.objects.get(id=res.data['id'])
    for k, v in payload.items():
        if k != 'geometry':
            self.assertEqual(getattr(river, k), v)
        else:
            geom_from_json = GEOSGeometry(json.dumps(v))
            db_geo = getattr(river, k)
            assert (db_geo.equals(geom_from_json))
    self.assertEqual(river.owner, self.user)

    def test_create_river_point(self):
        """Test creating a river"""
        # coordinates = []
        # coordinates.append([-159.55596127142, 63.8967914977418])
        payload = {
            "name": 'Test River 2',
            "feature": 'Stream',
            "state": 'OR',
            "region": 1,
            "miles": 47.3,
            "geometry": {
                'type': 'Point',
                'coordinates': [-159.55596127142, 63.8967914977418]
            }
        }
        res = self.client.post(RIVERS_URL, json.dumps(payload),
                               content_type='application/json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        river = River.objects.get(id=res.data['id'])
        for k, v in payload.items():
            if k != 'geometry':
                self.assertEqual(getattr(river, k), v)
            else:
                geom_from_json = GEOSGeometry(json.dumps(v))
                db_geo = getattr(river, k)
                assert (db_geo.equals(geom_from_json))
        self.assertEqual(river.owner, self.user)

    def test_partial_update(self):
        """Test partial update of a river."""
        coordinates = [
            (-159.55596127142, 63.8967914977418),
            (-159.55629960491, 63.8952464976259),
        ]
        lineString = LineString(coordinates, srid=4326)
        river = create_river(owner=self.user,
                             name='Owyhee',
                             geometry=lineString)

        payload = {'name': 'Deschutes'}
        url = detail_url(river.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        river.refresh_from_db()
        for k, v in payload.items():
            if k != 'geometry':
                self.assertEqual(getattr(river, k), v)
            else:
                geom_from_json = GEOSGeometry(json.dumps(v))
                db_geo = getattr(river, k)
                assert (db_geo.equals(geom_from_json))
        self.assertEqual(river.owner, self.user)

    def test_full_update(self):
        """Test full update of river"""
        coordinates = [
            (-159.55596127142, 63.8967914977418),
            (-159.55629960491, 63.8952464976259),
        ]
        lineString = LineString(coordinates, srid=4326)
        river = create_river(
            owner=self.user,
            feature='Stream',
            state='OR',
            region=1,
            miles=47.3,
            name='Owyhee',
            geometry=lineString,
        )

        payload = {
            'name': 'Test River',
            'feature': 'Stream',
            'state': 'CA',
            "region": 2,
            "miles": 43.7,
            "geometry": {
                "type": 'LineString',
                "coordinates": [[-157.55596127142, 63.8967914977418],
                                [-159.557151821688, 63.8904670545064]]
            },

        }
        url = detail_url(river.id)
        res = self.client.put(url, json.dumps(payload),
                              content_type='application/json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        river.refresh_from_db()
        for k, v in payload.items():
            if k != 'geometry':
                self.assertEqual(getattr(river, k), v)
            else:
                geom_from_json = GEOSGeometry(json.dumps(v))
                db_geo = getattr(river, k)
                assert (db_geo.equals(geom_from_json))
        self.assertEqual(river.owner, self.user)

    def test_update_user_returns_error(self):
        """Test changing the river user results in an error."""
        new_user = create_user(email='user2@example.com', password='test123')
        river = create_river(owner=self.user)

        payload = {'owner': new_user.id}
        url = detail_url(river.id)
        self.client.patch(url, payload)

        river.refresh_from_db()
        self.assertEqual(river.owner, self.user)

    def test_delete_river(self):
        """Test deleting a river succesful."""
        river = create_river(owner=self.user)

        url = detail_url(river.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(River.objects.filter(id=river.id).exists())

    def test_river_other_users_river_error(self):
        """Test trying to delete another users river gives. error."""
        new_user = create_user(email='user2@example.com', password='test123')
        river = create_river(owner=new_user)

        url = detail_url(river.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(River.objects.filter(id=river.id).exists())
