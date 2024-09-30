accessibility_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_general_stats_education",
            "description": "Returns statistics on everything related to education:"
            "[kindergartens, schools, specialized educational institutions, "
            "secondary special educational institutions, "
            "higher educational institutions]; data on the transport accessibility of all educational institutions.",
            "parameters": {
                "type": "object",
                "properties": {"coordinates": {"type": "dict"}},
                "required": ["coordinates"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_general_stats_healthcare",
            "description": "Returns statistics on all possible healthcare facilities for PEOPLE, "
            "everything related to human health: [clinics, "
            "polyclinics, hospitals, inpatient facilities, trauma departments, maternity homes, "
            "dentistry, women's consultations, pharmacies, emergency stations, "
            "psychological help centers]; data on the transport accessibility of all "
            "medical services.",
            "parameters": {
                "type": "object",
                "properties": {"coordinates": {"type": "dict"}},
                "required": ["coordinates"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_general_stats_culture",
            "description": "Returns statistics on the provision of cultural and leisure objects of all kinds: "
            "[libraries, museums, botanical gardens, circuses, theaters, zoos, cinemas, movie theaters, "
            "cafes, restaurants, parks, clubs, landmarks];"
            "data on the transport accessibility of all these objects by transport and on foot.",
            "parameters": {
                "type": "object",
                "properties": {"coordinates": {"type": "dict"}},
                "required": ["coordinates"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_general_stats_sports",
            "description": "Returns statistics on sports facilities, everything related to sports: "
            "[swimming pools, gyms, fitness centers, ice rinks, figure skating rinks, "
            "football fields, basketball courts]; data on the transport accessibility of all these facilities.",
            "parameters": {
                "type": "object",
                "properties": {"coordinates": {"type": "dict"}},
                "required": ["coordinates"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_general_stats_services",
            "description": "Returns statistics on objects that improve the quality of life, social services, objects providing "
            "various services, objects for pets: "
            "[grocery stores, clothing stores, electronics stores, bookstores, "
            "children's stores, banks, government service centers, hairdressers, "
            "beauty salons, veterinary clinics, dog walking areas]; data on the transport "
            "accessibility of all these objects.",
            "parameters": {
                "type": "object",
                "properties": {"coordinates": {"type": "dict"}},
                "required": ["coordinates"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_general_stats_demography",
            "description": "Returns statistics on demographic indicators: [population of the territory, "
            "population under working age (children), working age, over working age, pensioners; population growth "
            "over the last year; the number of preschool children, "
            "school-age children; expected number of pregnant women and population with children under one year; "
            "expected number of people with disabilities affecting motor skills, etc. "
            "Also, using the key 'Number of service types,' you can get information on the number of services corresponding to the indicators.",
            "parameters": {
                "type": "object",
                "properties": {"coordinates": {"type": "dict"}},
                "required": ["coordinates"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_general_stats_housing_and_communal_services",
            "description": "Returns statistics on such housing and communal services indicators as: total area "
            "of residential premises and per capita; the share of dilapidated and emergency housing; the share of residential buildings with "
            "central cold/hot water supply; the share of houses equipped with central sewage; "
            "the average age of residential buildings in the area; the number of emergency residential buildings, etc. "
            "Also, using the key 'Number of service types,' you can get information on the number of services corresponding to the indicators.",
            "parameters": {
                "type": "object",
                "properties": {"coordinates": {"type": "dict"}},
                "required": ["coordinates"],
            },
        },
    },
    # {
    #   "type": "function",
    #   "function": {
    #     "name": "get_general_stats_object",
    #     "description": "Returns general information about a selected object. If the query DOES NOT MENTION education, "
    #                    "healthcare, culture and leisure, sports, demography, housing and communal services, "
    #                    "various services for the population, only this function should be selected.",
    #     "parameters": {
    #       "type": "object",
    #       "properties": {
    #         "coordinates": {
    #           "type": "dict"
    #         }
    #       },
    #       "required": [
    #         "coordinates"
    #       ]
    #     }
    #  }
    # }
]
