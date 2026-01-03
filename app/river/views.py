"""
Views for the River APIs.
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import River
from river import serializers


class RiverViewSet(viewsets.ModelViewSet):
    """View for manage river APIs"""
    serializer_class = serializers.RiverDetailSerializer
    queryset = River.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve rivers for authenticated user."""
        # JMR - probably need to get rid of this function to return all rivers.
        return self.queryset.filter(owner=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.RiverSerializer

        # This will return the detail serializer which is
        # set at the top of the class.
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new river."""
        if serializer.is_valid():
            serializer.save(owner=self.request.user)
