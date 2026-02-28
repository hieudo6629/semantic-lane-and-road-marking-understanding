import openai
import json

class OpenAILLM:

    def __init__(self, api_key):
        openai.api_key = api_key

    def generate(self, structure):
        prompt = f"""
        You are a driving assistant.
        Based on the road structure:
        {json.dumps(structure)}
        Provide driving indication and reasoning.
        """

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return response["choices"][0]["message"]["content"]