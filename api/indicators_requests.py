from api.api import Api


def get_indicators(
    indicators: list[str],
    name_id: str | None = None,
    territory_type: str | None = None,
    coordinates: dict | None = None,
) -> dict:
    # coordinates must be prepared and typed via api.utils.coords_typer.prepare_typed_coords
    if not indicators:
        msg = "Expected at least one indicator"
        raise ValueError(msg)
    if name_id or coordinates:
        return Api.EndpointsIndicators.get_indicators(
            indicators=indicators,
            territory_name_id=name_id,
            territory_type=territory_type,
            selection_zone=coordinates,
        )
    msg = "Expected name_id or coordinates"
    raise ValueError(msg)
