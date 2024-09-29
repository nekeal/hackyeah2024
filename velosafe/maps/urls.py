from django.urls import include, path
from velosafe.maps.views import PreferencesFormView

app_name = "maps"

urlpatterns = [
    path(r"", PreferencesFormView.as_view(), name="map"),
]
