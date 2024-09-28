from string import Template

from django.views.generic import View, TemplateView
from django.shortcuts import render

from velosafe.maps.maps import MapService


# Create your views here.

class MapView(TemplateView):
    template_name = 'map.html'

    def get_map(self):
        map_service = MapService(starting_location=[49.477446198395675, 20.03088213331825], zoom_start=14)
        return map_service.get_html()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['map'] = self.get_map()
        return context


map_view = MapView.as_view()
