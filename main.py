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
import io
from PIL import Image
from datetime import datetime

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
import response_schemas


app = Flask(__name__, static_folder="static", static_url_path="")
MODEL_NAME=os.environ.get("MODEL_NAME", "gemini-2.5-flash")
CORS_ORIGINS = os.environ.get("CORS_ORIGINS")
if CORS_ORIGINS:
    CORS(app, resources={r"*": {"origins": CORS_ORIGINS }})
print(f"Service parameters: MODEL_NAME: {MODEL_NAME} CORS_ORIGINS: {CORS_ORIGINS}")

CNH = "CNH"
RG = "RG"
CN = "CN"
CC = "CC"

doc_config = {
    CNH: genai_util.getGenAiConfig(model_prompts.valida_CNH, response_schemas.CNH),
    RG: genai_util.getGenAiConfig(model_prompts.valida_RG, response_schemas.RG),
    CN: genai_util.getGenAiConfig(model_prompts.valida_CN, response_schemas.CN),
    CC: genai_util.getGenAiConfig(model_prompts.valida_CC, response_schemas.CC)
}

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
def read_doc() -> Response:
    docType = request.form.get("doc-type", "").upper()
    print(f"docType: {docType}")
    if not docType in doc_config:
        return returnError(f"Campo doc-type desconhecido. Recebido: {docType}")
    try:
        client = genai.Client(vertexai=True, location="global") #project=os.getenv("PROJECT_ID") -> pega do ambiente
        parts = []
        #parts.append(types.Part.from_text(text="siga as instruções"))
        parts.append(types.Part.from_text(text="siga as instruções"))
        parts.append(getDocumentPart(request))
        contents = [
            types.Content(
            role="user",
            parts=parts
            )
        ]
        response = client.models.generate_content(
            model = MODEL_NAME,
            contents = contents,
            config = doc_config[docType]
        )
        print(response.text)
        return Response(
                status=200,
                mimetype='application/json', 
                response=response.text
                )
    except Exception as e:
        logger.exception(e)
        return returnError(f"não foi possível ler o documento. Erro: {e}")

def returnError(error):
    return Response(
        status=400,
        response=error
    )

def getDocumentPart(request):
    if not request.files:
        raise Exception("Falta o documento")
    file_storage = next(iter(request.files.values()))
    rec_file_name = file_storage.filename
    file_name = uniquefy_filename(rec_file_name)
    logger.info(f"{file_name} - Received filename: {rec_file_name}")
    mime_type = ""
    file_path = os.path.join(tempfile.gettempdir(), file_name)  
    file_storage.save(file_path)
    mime_type = getMimeType(file_path)
    with open(file_path, "rb") as uploadfile:
        file_bytes = uploadfile.read()
    #file_bytes = file_storage.read()
    os.remove(file_path)
    logger.info(f"{file_name} - file is {mime_type}.")
    return types.Part(inline_data={"mime_type": mime_type,"data": file_bytes})

    #todas tentativas falhas de leitura
    #return Image.open(io.BytesIO(file_storage.read()))
    #return types.Part.from_data(mime_type=mime_type, data=file_bytes)
    #return types.Part(inline_data={"mime_type": mime_type,"data": io.BytesIO(file_storage.read())})
    #return types.Part(inline_data={"mime_type": mime_type,"data": file_storage.read()})
    

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
