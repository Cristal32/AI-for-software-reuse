import json
import pandas as pd
from groq import Groq

# Load API keys from config.json
with open("config.json") as f:
    config = json.load(f)

def call_groq_model(model_name, prompt):
  """ Call a Groq model API """
  client = Groq(
      api_key = config['groq']['api_key']
  )

  response = client.chat.completions.create(
      model=model_name,
      messages=[
          {
              "role": "user",
              "content": ("Analyse the code, if there is any comment asking to implement a method, implement it. Otherwise, fix any issues with it, "
                    "and propose solutions to avoid boilerplate code by implementing reusable code if possible. "
                    "Return only the refactored code between ``` symbols and don't send any other text:\n" + prompt)
          }
      ],
      temperature=1,
      max_tokens=1024,
      top_p=1,
      stream=False,
      stop=None,
  )

  return response

def refactor_code(original_code):
    """Envoyer le code original à l'API LLM pour refactoring."""
    response = call_groq_model("llama3-8b-8192", original_code)

    # Access the content attribute directly
    if response and response.choices:
        return response.choices[0].message.content
    else:
        return None
