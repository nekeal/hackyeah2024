from django.urls import include, path
from velosafe.maps.views import map_view


app_name = "maps"

urlpatterns = [
    path(r"", map_view, name="map"),
]
