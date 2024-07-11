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
    "description": "Возвращает статистику по обеспеченности всеми видами образовательных учреждений, такими как детские сады"
                   "школы, специализированные учебные заведения, средние специальные учебные заведения"
                   "высшие учебные заведения; данные по транспортной доступности всех образовательных учреждений.",
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
    "description": "Возвращает статистику по всем возможным параметрам здравоохранения, таким как: обеспеченность клиниками, "
                  "поликлиниками, больницами, детскими поликлиниками, детскими стационарами, травматологическими "
                  "отделениями, родильными домами, стоматологиями, женскими консультациями, аптеками, станциями скорой "
                  "помощи, центрами психологической помощи; данные о транспортной доступности всех медицинских услуг на "
                  "различных видах общественного и личного транспорта, а также пешком.",
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
    "description": "Возвращает статистику по обеспеченности объектами культуры и досуга всех видов, такими как: библиотеки, музеи,"
                   "ботанические сады, цирки, театры, зоопарки, кинотеатры, кинозалы, кафе, рестораны, парки;"
                   "данные о транспортной доступности всех этих объектов на транспорте и пешком",
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
    "description": "Возвращает статистику по обеспеченности объектами всех видов спортивной инфраструктуры, такими как бассейны, "
                   "тренажерные залы, фитнес-центры, ледовые катки, катки, катки для фигурного катания,"
                   " футбольные поля; данные о транспортной доступности всех этих объектов на различных видах "
                   "общественного и личного транспорта, а также пешком",
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
    "description": "Возвращает статистику по предоставлению таких услуг, как: продуктовые магазины, обувные магазины,"
                  "магазины с одеждой, магазины бытовой техники, книжные магазины, детские магазины, банки, "
                  "многофункциональные центры оказания государственных и муниципальных услуг населению, парикмахерские, "
                  "салоны красоты, ветеринарные клиники, площадки для выгула собак; данные о транспортной "
                  "доступности всех этих объектов на разных видах общественного и личного транспорта и пешком",
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
