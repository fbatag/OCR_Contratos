#from google import genai
from google.genai import types

def getGenAiConfig(general_instructions):
    return types.GenerateContentConfig(
        temperature = 0.5,
        safety_settings = [types.SafetySetting(
              category="HARM_CATEGORY_HATE_SPEECH",
              threshold="OFF"
            ),types.SafetySetting(
              category="HARM_CATEGORY_DANGEROUS_CONTENT",
              threshold="OFF"
            ),types.SafetySetting(
              category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
              threshold="OFF"
            ),types.SafetySetting(
              category="HARM_CATEGORY_HARASSMENT",
              threshold="OFF"
        )],
        system_instruction=[types.Part.from_text(text=general_instructions)],
        thinking_config=types.ThinkingConfig(
          thinking_budget=128,
        ),
    )
