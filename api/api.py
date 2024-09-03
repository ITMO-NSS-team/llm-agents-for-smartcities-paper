from inspect import ismethod
import os

from dotenv import load_dotenv
from models.definitions import ROOT

from api.endpoint import GetEndpoint
from api.endpoint import PostEndpoint


load_dotenv(ROOT / "config.env")


class Api:
    class EndpointsListings:
        _base_url = os.environ.get("ENDPOINT_LISTINGS_URL")
        cities = GetEndpoint("/api/list/cities", param_names=("centers_only",))
        cities_statistics = GetEndpoint("/api/list/cities_statistics", param_names=())
        city_service_type_living_situations = GetEndpoint(
            "/api/list/city_service_type/{city_service_type_id}/living_situations",
            param_names=("city_service_type_id",),
        )
        city_service_types = GetEndpoint("/api/list/city_service_types", param_names=())

    class EndpointsCity:
        _base_url = os.environ.get("ENDPOINT_CITY_URL")
        municipalities = GetEndpoint(
            "/api/city/{city}/municipalities",
            param_names=("city", "centers_only"),
        )
        districts = GetEndpoint(
            "/api/city/{city}/administrative_units",
            param_names=("city", "centers_only"),
        )
        # Receives city code or city name in Russian
        territories = GetEndpoint(
            "/api/city/{city}/territories",
            param_names=("city", "centers_only"),
        )
        houses = GetEndpoint(
            "/api/city/{city}/houses",
            param_names=(
                "city",
                "geometryAsCenter",
                "livingOnly",
                "requiredProperties",
            ),
        )
        blocks = GetEndpoint(
            "/api/city/{city}/blocks", param_names=("city", "centers_only")
        )

    class EndpointsMetrics:
        _base_url = os.environ.get("ENDPOINT_METRICS_URL")
        blocks_accessibility = GetEndpoint(
            url="/api/v2/blocks_accessibility/get_accessibility",
            param_names=("city", "block_id"),
        )

    class EndpointsProvision:
        _base_url = os.environ.get("ENDPOINT_PROVISION_URL")
        get_provision = PostEndpoint(
            url="/api_v3/get_provision/",
            param_names=(
                "city",
                "service_types",
                "year",
                "calculation_type",
                "user_selection_zone",
                "valuation_type",
                "service_impotancy",
            ),
        )

    class EndpointsSummaryTables:
        _base_url = os.environ.get("ENDPOINT_SUMMARY_URL")
        get_summary_table = PostEndpoint(
            url="/api_llm/tables_context/",
            param_names=(
                "table",
                "territory_name_id",
                "territory_type",
                "selection_zone",
            ),
        )


# Process all endpoint groups to set base url
for endpoint_group_name in dir(Api):
    if not endpoint_group_name.startswith("Endpoints"):
        continue
    endpoint_group = getattr(Api, endpoint_group_name)

    for endpoint_name in dir(endpoint_group):
        if ismethod(getattr(endpoint_group, endpoint_name)) or endpoint_name.startswith(
            "_"
        ):
            continue
        endpoint = getattr(endpoint_group, endpoint_name)
        endpoint.url = endpoint_group._base_url + endpoint.url
