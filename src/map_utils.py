import math

import pandas as pd
import pydeck as pdk


AIRPORTS_PATH = "data/airports.csv"
HUB = "BRU"


# --------------------------------------------------
# Market-type colors
# --------------------------------------------------

MARKET_COLORS = {
    "business": [70, 150, 255, 220],
    "mixed": [170, 110, 255, 220],
    "leisure": [255, 100, 120, 220],
}


def calculate_view_state(
    hub_latitude,
    hub_longitude,
    destination_data,
):
    """
    Automatically center and zoom the map
    around the currently selected network.
    """

    if destination_data.empty:

        return pdk.ViewState(
            latitude=hub_latitude,
            longitude=hub_longitude,
            zoom=5.5,
            pitch=20,
            bearing=0,
        )

    latitudes = [
        hub_latitude,
        *destination_data[
            "latitude"
        ].tolist(),
    ]

    longitudes = [
        hub_longitude,
        *destination_data[
            "longitude"
        ].tolist(),
    ]

    min_latitude = min(latitudes)
    max_latitude = max(latitudes)

    min_longitude = min(longitudes)
    max_longitude = max(longitudes)

    center_latitude = (
        min_latitude
        + max_latitude
    ) / 2

    center_longitude = (
        min_longitude
        + max_longitude
    ) / 2

    latitude_span = (
        max_latitude
        - min_latitude
    )

    longitude_span = (
        max_longitude
        - min_longitude
    )

    max_span = max(
        latitude_span,
        longitude_span,
        1,
    )

    # Approximate automatic zoom.
    zoom = (
        7.8
        - math.log2(max_span)
    )

    zoom = max(
        2.2,
        min(
            zoom,
            5.5,
        ),
    )

    return pdk.ViewState(
        latitude=center_latitude,
        longitude=center_longitude,
        zoom=zoom,
        pitch=20,
        bearing=0,
    )


def build_network_map(
    active_routes,
):
    """
    Build an interactive map of Aerofrite's
    optimized weekly route network.

    Route styling communicates:

    - market type through color
    - weekly frequency through line thickness
    - commercial and operational metrics
      through tooltips
    """

    # --------------------------------------------------
    # Load airport coordinates
    # --------------------------------------------------

    airports = pd.read_csv(
        AIRPORTS_PATH
    )

    hub_rows = airports[
        airports["iata"] == HUB
    ]

    if len(hub_rows) != 1:

        raise ValueError(
            f"Expected exactly one {HUB} airport, "
            f"found {len(hub_rows)}."
        )

    hub = hub_rows.iloc[0]

    hub_latitude = float(
        hub["latitude"]
    )

    hub_longitude = float(
        hub["longitude"]
    )

    # --------------------------------------------------
    # Prepare active route data
    # --------------------------------------------------

    routes = active_routes.copy()

    if routes.empty:

        destination_data = pd.DataFrame(
            columns=[
                "route_id",
                "destination",
                "market_type",
                "frequency",
                "passengers",
                "load_factor",
                "contribution",
                "aircraft_hours",
                "iata",
                "name",
                "city",
                "latitude",
                "longitude",
            ]
        )

    else:

        # Example:
        # BRU-LHR -> LHR
        routes["destination"] = (
            routes[
                "route_id"
            ]
            .str.split("-")
            .str[-1]
        )

        destination_data = routes.merge(
            airports[
                [
                    "iata",
                    "name",
                    "city",
                    "latitude",
                    "longitude",
                ]
            ],
            left_on="destination",
            right_on="iata",
            how="left",
        )

        # --------------------------------------------------
        # Validate coordinates
        # --------------------------------------------------

        missing_coordinates = (
            destination_data[
                destination_data[
                    "latitude"
                ].isna()
                |
                destination_data[
                    "longitude"
                ].isna()
            ]
        )

        if not missing_coordinates.empty:

            missing_airports = (
                missing_coordinates[
                    "destination"
                ]
                .tolist()
            )

            raise ValueError(
                "Missing map coordinates for: "
                f"{missing_airports}"
            )

        # --------------------------------------------------
        # Add visual properties
        # --------------------------------------------------

        destination_data[
            "route_color"
        ] = destination_data[
            "market_type"
        ].map(
            MARKET_COLORS
        )

        # Line width reflects weekly frequency.
        #
        # 3/week  -> 2.5
        # 4/week  -> 3.0
        # 7/week  -> 4.5
        # 10/week -> 6.0
        # 14/week -> 8.0
        destination_data[
            "line_width"
        ] = (
            1
            + destination_data[
                "frequency"
            ] * 0.5
        )

        # --------------------------------------------------
        # Tooltip display values
        # --------------------------------------------------

        destination_data[
            "load_factor_display"
        ] = (
            destination_data[
                "load_factor"
            ]
            .map(
                lambda value:
                f"{value:.1%}"
            )
        )

        destination_data[
            "contribution_display"
        ] = (
            destination_data[
                "contribution"
            ]
            .map(
                lambda value:
                f"€{value:,.0f}"
            )
        )

        destination_data[
            "passengers_display"
        ] = (
            destination_data[
                "passengers"
            ]
            .map(
                lambda value:
                f"{int(value):,}"
            )
        )

        destination_data[
            "aircraft_hours_display"
        ] = (
            destination_data[
                "aircraft_hours"
            ]
            .map(
                lambda value:
                f"{value:.1f}"
            )
        )

        destination_data[
            "frequency_display"
        ] = (
            destination_data[
                "frequency"
            ]
            .map(
                lambda value:
                f"{int(value)}x/week"
            )
        )

    # --------------------------------------------------
    # Build route arc data
    # --------------------------------------------------

    if destination_data.empty:

        arc_data = pd.DataFrame(
            columns=[
                "route_id",
                "iata",
                "city",
                "market_type",
                "frequency",
                "frequency_display",
                "passengers_display",
                "load_factor_display",
                "contribution_display",
                "aircraft_hours_display",
                "line_width",
                "route_color",
                "source_latitude",
                "source_longitude",
                "target_latitude",
                "target_longitude",
            ]
        )

    else:

        arc_data = destination_data[
            [
                "route_id",
                "iata",
                "name",
                "city",
                "market_type",
                "frequency",
                "frequency_display",
                "passengers_display",
                "load_factor_display",
                "contribution_display",
                "aircraft_hours_display",
                "line_width",
                "route_color",
                "latitude",
                "longitude",
            ]
        ].copy()

        arc_data[
            "source_latitude"
        ] = hub_latitude

        arc_data[
            "source_longitude"
        ] = hub_longitude

        arc_data = arc_data.rename(
            columns={
                "latitude": (
                    "target_latitude"
                ),
                "longitude": (
                    "target_longitude"
                ),
            }
        )

    # --------------------------------------------------
    # Destination airport layer
    # --------------------------------------------------

    destination_layer = pdk.Layer(
        "ScatterplotLayer",
        data=destination_data,
        get_position=(
            "[longitude, latitude]"
        ),
        get_radius=28000,
        get_fill_color="route_color",
        get_line_color=[
            255,
            255,
            255,
            180,
        ],
        line_width_min_pixels=1,
        stroked=True,
        pickable=True,
        auto_highlight=True,
    )

    # --------------------------------------------------
    # Brussels hub
    # --------------------------------------------------

    hub_data = pd.DataFrame(
        [
            {
                "iata": HUB,
                "name": hub["name"],
                "city": hub["city"],
                "latitude": hub_latitude,
                "longitude": hub_longitude,
            }
        ]
    )

    hub_layer = pdk.Layer(
        "ScatterplotLayer",
        data=hub_data,
        get_position=(
            "[longitude, latitude]"
        ),
        get_radius=45000,
        get_fill_color=[
            255,
            200,
            50,
            255,
        ],
        get_line_color=[
            255,
            255,
            255,
            255,
        ],
        line_width_min_pixels=2,
        stroked=True,
        pickable=False,
    )

    # --------------------------------------------------
    # Route arcs
    # --------------------------------------------------

    arc_layer = pdk.Layer(
        "ArcLayer",
        data=arc_data,
        get_source_position=(
            "[source_longitude, "
            "source_latitude]"
        ),
        get_target_position=(
            "[target_longitude, "
            "target_latitude]"
        ),
        get_source_color=[
            255,
            200,
            50,
            210,
        ],
        get_target_color="route_color",
        get_width="line_width",
        width_min_pixels=1,
        width_max_pixels=10,
        pickable=True,
        auto_highlight=True,
    )

    # --------------------------------------------------
    # Airport labels
    # --------------------------------------------------

    label_data = destination_data[
        [
            "iata",
            "latitude",
            "longitude",
        ]
    ].copy()

    label_data = pd.concat(
        [
            label_data,
            hub_data[
                [
                    "iata",
                    "latitude",
                    "longitude",
                ]
            ],
        ],
        ignore_index=True,
    )

    label_layer = pdk.Layer(
        "TextLayer",
        data=label_data,
        get_position=(
            "[longitude, latitude]"
        ),
        get_text="iata",
        get_size=14,
        get_color=[
            255,
            255,
            255,
            255,
        ],
        get_pixel_offset=[
            0,
            -18,
        ],
        get_text_anchor="'middle'",
        get_alignment_baseline="'center'",
        pickable=False,
    )

    # --------------------------------------------------
    # Automatically fit map to network
    # --------------------------------------------------

    view_state = calculate_view_state(
        hub_latitude=hub_latitude,
        hub_longitude=hub_longitude,
        destination_data=destination_data,
    )

    # --------------------------------------------------
    # Route tooltip
    # --------------------------------------------------

    tooltip = {
        "html": (
            "<b>{route_id}</b>"
            "<br/>"
            "{city} ({iata})"
            "<br/><br/>"
            "<b>Market:</b> {market_type}"
            "<br/>"
            "<b>Frequency:</b> "
            "{frequency_display}"
            "<br/>"
            "<b>Passengers:</b> "
            "{passengers_display}"
            "<br/>"
            "<b>Load factor:</b> "
            "{load_factor_display}"
            "<br/>"
            "<b>Contribution:</b> "
            "{contribution_display}"
            "<br/>"
            "<b>Aircraft hours:</b> "
            "{aircraft_hours_display}"
        ),
        "style": {
            "backgroundColor": "#1f2937",
            "color": "white",
            "fontSize": "13px",
        },
    }

    # --------------------------------------------------
    # Final map
    # --------------------------------------------------

    deck = pdk.Deck(
        layers=[
            arc_layer,
            destination_layer,
            hub_layer,
            label_layer,
        ],
        initial_view_state=view_state,
        map_provider="carto",
        map_style="dark",
        tooltip=tooltip,
    )

    return deck