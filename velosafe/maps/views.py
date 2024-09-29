from django import forms
from django.core.cache import cache
from django.http import HttpResponse
from django.views import View
from django.views.generic import TemplateView, FormView

from velosafe.route_planning.facade import GeneralRoadTypes, RoutePlanningFacade, RoutePlanningInput, \
    RoutePlanningPreferences

from velosafe.maps.maps import MapService
from velosafe.route_planning.point import Point
from velosafe.utils import get_hash


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
    street_light = forms.BooleanField(label="Street light", required=False, initial=True)
    allowed_road_types = forms.MultipleChoiceField(
        label="Allowed road types",
        choices=GeneralRoadTypes.choices,
        widget=forms.CheckboxSelectMultiple,
        initial=[GeneralRoadTypes.bike_path]
    )
    safety_factor = forms.IntegerField(label="Safety factor", min_value=1, max_value=5, initial=3)
    bike_path_preference = forms.IntegerField(label="Bike path preference", min_value=1, max_value=5, initial=3)

class PreferencesFormView(FormView):
    template_name = "preferences_form.html"
    success_url = "/"
    form_class = PreferencesForm


    def form_invalid(self, form):
        print(form.errors, form.data, "form invalid")
        print(form.data)
        return super().form_invalid(form)

    def form_valid(self, form):
        points = self.request.POST.getlist("points[]")
        facade_input = RoutePlanningInput(points=[Point(float(x),float(y)) for x,y in zip(points[:-1:2], points[1::2])], preference=RoutePlanningPreferences(
            max_allowed_speed=form.cleaned_data["max_allowed_speed"],
            street_light=form.cleaned_data["street_light"],
            allowed_road_types=form.cleaned_data["allowed_road_types"],
            safety_factor=form.cleaned_data["safety_factor"],
        ))
        result = RoutePlanningFacade().plan_route(facade_input)
        # print("Respone", result, type(result))
        return HttpResponse(result)


class UserRouteView(View):

    def get(self, request, *args, **kwargs):
        form = PreferencesForm(request.GET)
        form.is_valid()
        points = self.request.GET.getlist("points[]")
        facade_input = RoutePlanningInput(points=[Point(float(x),float(y)) for x,y in zip(points[:-1:2], points[1::2])], preference=RoutePlanningPreferences(
            max_allowed_speed=form.cleaned_data["max_allowed_speed"],
            street_light=form.cleaned_data["street_light"],
            allowed_road_types=form.cleaned_data["allowed_road_types"],
            bike_path_preference=form.cleaned_data["bike_path_preference"],
            safety_factor=form.cleaned_data["safety_factor"],
        ))
        cache_key = get_hash(facade_input)
        if result := cache.get(cache_key):
            return HttpResponse(result)
        result = RoutePlanningFacade().plan_route(facade_input)
        cache.set(cache_key, result)
        return HttpResponse(result)