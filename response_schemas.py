CNH = {
  "properties": {
    "cpf": {
      "type": "string",
      "description": "Número do Cadastro de Pessoas Físicas (CPF)."
    },
    "name": {
      "type": "string",
      "description": "Nome completo do indivíduo."
    },
    "father_name": {
      "type": "string",
      "description": "Nome do pai."
    },
    "mother_name": {
      "type": "string",
      "description": "Nome da mãe."
    },
    "birth_date": {
      "type": "string",
      "description": "Data de nascimento."
    },
    "expiration": {
      "type": "string",
      "description": "Data de validade do documento ou cadastro."
    },
    "valid": {
      "type": "string",
      "description": "Indica se o cadastro está válido.",
      "enum": [
        "sim",
        "nao",
        "suspeito"
      ]
    }
  }
}

RG = {}
CN = {}
CC = {}
