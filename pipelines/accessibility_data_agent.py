import json
import requests
from pprint import pprint


# model_url = 'http://10.32.2.2:8673/v1/chat/completions'  # meta-llama3-8b-q8-function-calling
model_url = 'http://10.32.2.2:8671/v1/chat/completions'  # Meta-Llama-3-70B-Instruct-v2.Q4_K_S

question = 'Насколько люди обеспечены объектами здравоохранения?'
question = 'Какова средняя доступность травматологических отделений на общественном транспорте?'
question = 'Какова средняя доступность магазинов детских товаров на общественном транспорте?'

extra_data = 'Coordinates: {"type": "polygon", "coords": [[[30.688828198781902, 59.775976109763285]]]}, territory type: city.'

tools = [
{
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
},
{
  "type": "function",
  "function": {
    "name": "get_general_stats_districs_mo",
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
},
{
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
},
{
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
},
{
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
},
{
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
},
{
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
},
{
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
]

params = {
  # "model": "gpt-3.5-turbo",
  "messages": [
    {
      "role": "system",
      # "content": "You are a smart AI assistant, You have high expertise in the field of "
      #            "urbanistics and structure of Saint Petersburg. "
      "content": f"You are a helpful assistant with access to the following functions. "
                 f"Use them if required - {str(tools)}."
    },
    {
      "role": "user",
      # "content": f"You have access to a database with several tables that contain statistics for different types "
      #            f"of territories. Please choose a function to extract information that is needed to answer the "
      #            f"following question: {question}\n"
      #            f"Extra information: {extra_data}"
      "content": f"Extract all relevant data for answering this question: "
                 f"{question}\n Extra information: {extra_data}"
                 f"Please only return the function call with parameters."
    }
  ]
}

response = requests.post(url=model_url, json=params)
res = json.loads(response.text)

pprint(res)
pprint(json.loads(res['choices'][0]['message']['content']))
