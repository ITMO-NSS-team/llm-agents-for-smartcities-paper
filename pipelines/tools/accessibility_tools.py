get_general_stats_city_tool = {
  "type": "function",
  "function": {
    "name": "get_general_stats_city",
    "description": "Get statistics for healthcare, population, housing facilities, recreation, playgrounds, "
                   "education, public transport accessibility, churches and temples, sports infrastructure,"
                   "cultural and leisure facilities in the given city.",
    "parameters": {
      "type": "object",
      "properties": {
        "coordinates": {
          "type": "dict"
        }
      },
      "required": [
        "coordinates"
      ]
    }
  }
}

get_general_stats_districts_mo_tool = {
  "type": "function",
  "function": {
    "name": "get_general_stats_districts_mo",
    "description": "Get statistics for healthcare, education, public transport accessibility, churches and "
                   "temples, sports infrastructure, cultural and leisure facilities in the given district or "
                   "municipality.",
    "parameters": {
      "type": "object",
      "properties": {
        "coordinates": {
          "type": "dict"
        }
      },
      "required": [
        "coordinates"
      ]
    }
  }
}

get_general_stats_block_tool = {
  "type": "function",
  "function": {
    "name": "get_general_stats_block",
    "description": "Get statistics for healthcare, population, housing facilities, recreation, playgrounds, "
                   "education, public transport accessibility, churches and temples, sports infrastructure,"
                   "cultural and leisure facilities in the given city.",
    "parameters": {
      "type": "object",
      "properties": {
        "coordinates": {
          "type": "dict"
        }
      },
      "required": [
        "coordinates"
      ]
    }
  }
}

get_general_stats_education_tool = {
  "type": "function",
  "function": {
    "name": "get_general_stats_education",
    "description": "Get statistics for the provision of educational facilities like kindergarten,"
                   "schools, specialized educational institutions, higher education institution. Get"
                   "statistics about public transport accessibility of educational institutions.",
    "parameters": {
      "type": "object",
      "properties": {
        "coordinates": {
          "type": "dict"
        }
      },
      "required": [
        "coordinates"
      ]
    }
  }
}

get_general_stats_healthcare_tool = {
  "type": "function",
  "function": {
    "name": "get_general_stats_healthcare",
    "description": "Get statistics for various healthcare parameters like: provision of clinics, hospitals,"
                   "trauma departments, maternity hospitals/wards, dental clinics, female consultation clinics,"
                   "pharmacies, ambulances; get transport accessibility of all healthcare services.",
    "parameters": {
      "type": "object",
      "properties": {
        "coordinates": {
          "type": "dict"
        }
      },
      "required": [
        "coordinates"
      ]
    }
  }
}

get_general_stats_culture_tool = {
  "type": "function",
  "function": {
    "name": "get_general_stats_culture",
    "description": "Get statistics for the provision of cultural and leisure facilities like: libraries, museums,"
                   "botanical gardens, circuses, theaters, zoos, movie theaters, restaurants; get transport "
                   "accessibility of all these facilities.",
    "parameters": {
      "type": "object",
      "properties": {
        "coordinates": {
          "type": "dict"
        }
      },
      "required": [
        "coordinates"
      ]
    }
  }
}

get_general_stats_sports_tool = {
  "type": "function",
  "function": {
    "name": "get_general_stats_sports",
    "description": "Get statistics for the provision of sports infrastructure facilities like: swimming pools "
                   "and gyms; get transport accessibility of all these facilities.",
    "parameters": {
      "type": "object",
      "properties": {
        "coordinates": {
          "type": "dict"
        }
      },
      "required": [
        "coordinates"
      ]
    }
  }
}

get_general_stats_services_tool = {
  "type": "function",
  "function": {
    "name": "get_general_stats_services",
    "description": "Get statistics for the provision of services like: grocery stores, clothing stores, "
                   "home appliance stores, book stores, children's stores, banks, multifunctional centers for "
                   "the provision of state and municipal services, hairdresser's and beauty salons, veterinarian "
                   "clinics, dog playgrounds; get transport accessibility of all these facilities.",
    "parameters": {
      "type": "object",
      "properties": {
        "coordinates": {
          "type": "dict"
        }
      },
      "required": [
        "coordinates"
      ]
    }
 }
}
