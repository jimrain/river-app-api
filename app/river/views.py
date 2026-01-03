"""
Views for the River APIs.
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from core.models import River
from core.permissions import IsOwnerOrReadOnly
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
        return self.queryset.order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.RiverSerializer

        # This will return the detail serializer which is
        # set at the top of the class.
        return self.serializer_class

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions
        that this view requires.
        """
        if self.action == 'list':
            # All users can list
            permission_classes = [AllowAny]
        elif self.action in ['update', 'partial_update',
                             'destroy', 'retrieve']:
            # Only owner can modify/view detail
            permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
        else:
            # For create (POST), only authenticated users can add
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Create a new river."""
        if serializer.is_valid():
            serializer.save(owner=self.request.user)
