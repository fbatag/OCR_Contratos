# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#from IPython.display import Markdown
from google import genai
from google.genai import types
from datetime import date, datetime

import os
import tempfile
import filetype
import json
import base64 # Import base64 module

import signal
import sys
from types import FrameType

from flask import Flask, render_template, request, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
from flask_swagger_ui import get_swaggerui_blueprint
from yaml import Loader, load

import middleware
import genai_util
from middleware import jwt_authenticated, logger
import model_prompts


app = Flask(__name__, static_folder="static", static_url_path="")
MODEL_NAME=os.environ.get("MODEL_NAME", "gemini-2.5-flash")
CORS_ORIGINS = os.environ.get("CORS_ORIGINS")
if CORS_ORIGINS:
    CORS(app, resources={r"*": {"origins": CORS_ORIGINS }})
print(f"Service parameters: MODEL_NAME: {MODEL_NAME} CORS_ORIGINS: {CORS_ORIGINS}")

client = genai.Client(vertexai=True, location="global") #project=os.getenv("PROJECT_ID") -> pega do ambiente
valida_documentos_config = genai_util.getGenAiConfig(model_prompts.valida_documentos)
valida_titular_config = genai_util.getGenAiConfig(model_prompts.valida_titular)

### swagger specific ###
SWAGGER_URL = '/docs'
swagger_yml = load(open('./static/openapi.yaml', 'r'), Loader=Loader)
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL,'/static/openapi.yaml',
    config={
        'spec': swagger_yml
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route("/", methods=["POST"])
@jwt_authenticated
def val_docs() -> Response:
    return valida(request, "doc")

@app.route("/val_tit", methods=["POST"])
@jwt_authenticated
def val_tit() -> Response:
    return valida(request, "")
        
def valida(request, operacao):
    try:
        parts = []
        parts.append(types.Part.from_text(text=getPrompt(request, operacao)))
        parts.extend(getDocumentsParts(request))
        response = getResponse(valida_documentos_config, parts)
        if not response:
            return returnError()
        return Response(
                status=200,
                mimetype='application/json', 
                response=response
                )
    except Exception as e:
        logger.exception(e)
        return returnError()

def returnError():
    return Response(
        status=400,
        response="Unable to analyze the data! Please check the "
        "application logs for more details.",
    )

def getPrompt(request, operacao):
    titular, nro_dep = getDadosValidacao(request)
    if operacao == "doc":
        return f"""Titular: {titular} 
            Quantidade de dependentes: {str(nro_dep)} 
            Data de hoje: {date.today().strftime('%d/%m/%Y')}
            Documentos:"""
    return f"""Titular: {titular} 
        Data de hoje: {date.today().strftime('%d/%m/%Y')}
        Documentos:""" 

def getResponse(config, parts):
    contents = [
        types.Content(
          role="user",
          parts=parts
        ),
    ]
    response = client.models.generate_content(
        model = MODEL_NAME,
        contents = contents,
        config = config
    )
    print(response.text)
    return response.text

def getDocumentsParts(request):
    documentParts = []
    files = request.files.to_dict()
    for rec_file_name, file in files.items():
        file_name = uniquefy_filename(rec_file_name)
        logger.info(f"{file_name} - Received filename: {rec_file_name}")
        mime_type = ""
        try:
            file_path = os.path.join(tempfile.gettempdir(), file_name)  
            file.save(file_path)
            mime_type = getMimeType(file_path)
            with open(file_path, "rb") as uploadfile:
                file_bytes = uploadfile.read()
            os.remove(file_path)
            #logger.info(f"{file_name} - file is {mime_type}.")
            documentParts.append(types.Part(
                            inline_data={
                                "mime_type": mime_type,
                                "data": file_bytes
                                }            
                            ))
        except Exception as e:
            logger.warning(f"{file_name}:{mime_type} -  error: {e}")
     
    return documentParts

def getDadosValidacao(request):
    return request.form.get("nome_titular","ERIC ALVES SILVA"), int(request.form.get("quantidade_dependentes",0))

def uniquefy_filename(filename):
    file_name_ext = secure_filename(filename).split('.')
    string_data = datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')
    file_name = file_name_ext[0] + "_" + string_data
    if len(file_name_ext) > 1:
        file_name += "." + file_name_ext[1]
    return file_name

def getMimeType(file_path):
    try:
        content_type = filetype.guess(file_path)
        mime = content_type.mime
        type = mime.split('/')[0]
    except Exception as e:
        raise Exception(f"Não foi possível determinar o tipo do conteúdo: {e}")
    if type != 'image' and mime != 'application/pdf':
        raise Exception(f"O tipo de arquivo {mime} não é suportado")
    return mime

def shutdown_handler(signal: int, frame: FrameType) -> None:
    logger.info("Signal received, safely shutting down.")
    middleware.logging_flush()
    print("Exiting process.", flush=True)
    sys.exit(0)

if __name__ == "__main__":
    # handles Ctrl-C locally
    signal.signal(signal.SIGINT, shutdown_handler)

    app.run(host="127.0.0.1", port=8080, debug=True)
else:
    # handles Cloud Run container termination
    signal.signal(signal.SIGTERM, shutdown_handler)
# [END cloudrun_sigterm_handler]
