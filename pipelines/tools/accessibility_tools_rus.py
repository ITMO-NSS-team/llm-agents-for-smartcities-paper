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

get_general_stats_demography_tool = {
  "type": "function",
  "function": {
    "name": "get_general_stats_demography",
    "description": "Возвращает статистику по демографическим показателям, таким как: численность населения территории; "
                  "численность населения моложе трудоспособного возраста, трудоспособного возраста, старше трудоспособного "
                  "возраста, пенсионеров; прирост населения территории за последний год; численность детей дошкольного возраста, "
                  "школьного возраста;  ожидаемая численность беременных женщин и населения с детьми до одного года; "
                  "ожидаемая численность инвалидов по опорного-двигательному аппарату и т.п.",
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

get_general_stats_housing_and_communal_services_tool = {
  "type": "function",
  "function": {
    "name": "get_general_stats_housing_and_communal_services",
    "description": "Возвращает статистику по таким позателям жилья и жилищно-коммунального хозяйства, как: общая площадь "
                  "жилых помещений и в расчете на одного жителя; доля ветхого и аварийного жилья; доля жилых домов с "
                  "центральным холодным/горячим водоснабжением; доля домов, обеспеченных центральной канализиацией; "
                  "средний возраст жилых домой на территории; количество аварийных жилых домов и т.п.",
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

get_general_stats_object_tool = {
  "type": "function",
  "function": {
    "name": "get_general_stats_object",
    "description": "Возвращает такую информацию по выбранному объекту, как: адрес объекта, параметры объекта, "
                  "удаленность объекта от метро, наиболее упоминаемые проблемы объекта и т.п.",
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
