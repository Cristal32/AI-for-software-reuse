import json
from groq import Groq
import openai

# Load API keys from config.json
with open("config.json") as f:
    config = json.load(f)

def call_openai_model(model_name, prompt):
    """ Call an OpenAI model API """
    openai.api_key = config['openai']['api_key']

    response = openai.ChatCompletion.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are an AI assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1024,
        top_p=1.0,
    )
    return response

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
    
def get_recommendation(input_code, snippets):
    # Construire la liste des snippets
    snippets_text = "\n".join(
        f"Snippet {i+1}:\n{snippet['code']}\nDescription: {snippet['description']}\n"
        for i, snippet in enumerate(snippets)
    )
    # Construire le prompt
    prompt = (
        "Here is an input code:\n\n"
        f"{input_code}\n\n"
        "This request is in the context of a smart repository where users store code snippets to be reused in their code later on."
        "Below are some code snippets. Your task is to choose the best snippet out of these that matches the functionality or complements the input code. "
        f"{snippets_text}"
        "Provide the following information:\n"
        "1. The suggested snippet, choose the snippet that fits for the input, if no snippet is useful, say so.\n"
        "2. How to integrate it into the input code (provide the full implemented code).\n"
        "Respond in the format:\n"
        "Voici le snippet suggéré:\n<suggested_snippet>\n\nComment l'intégrer:\n<integrated_code>\n\n"
        "The integrated code should use the code snippet as proof that it was the best suggestion"
    )

    # Appeler le modèle Llama
    response = call_openai_model("gpt-4", prompt)

    # Extraire et structurer la réponse
    if response and hasattr(response, "choices") and response.choices:
        content = response.choices[0].message.content
        if content:
            return content.strip("```").strip()
        else:
            return None
    else:
        return None
