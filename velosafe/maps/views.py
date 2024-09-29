from django import forms
from django.views.generic import TemplateView, FormView, CreateView

from velosafe.route_planning.facade import GeneralRoadTypes

from velosafe.maps.maps import MapService


class MapView(TemplateView):
    template_name = "map.html"

    def get_map(self):
        map_service = MapService(starting_location=[49.477446198395675, 20.03088213331825], zoom_start=14)
        return map_service.get_html()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["map"] = self.get_map()
        return context


map_view = MapView.as_view()


class PreferencesForm(forms.Form):
    max_allowed_speed = forms.IntegerField(label="Max allowed speed", min_value=20, max_value=120, initial=50)
    street_light = forms.BooleanField(label="Street light", required=True, initial=False)
    allowed_road_types = forms.MultipleChoiceField(
        label="Allowed road types",
        choices=GeneralRoadTypes.choices,
        widget=forms.CheckboxSelectMultiple,
    )
    safety_factor = forms.IntegerField(label="Safety factor", min_value=1, max_value=5, initial=3)
    bike_path_preference = forms.IntegerField(label="Bike path preference", min_value=1, max_value=5, initial=3)

class PreferencesFormView(FormView):
    template_name = "preferences_form.html"
    success_url = "/"
    form_class = PreferencesForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PreferencesForm(self.request.GET)
        return context

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):

