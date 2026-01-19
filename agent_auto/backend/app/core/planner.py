import os
from openai import OpenAI
from anthropic import Anthropic

client_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client_anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def plan(task: str, tools: dict):
    """
    Retorna:
    {
      "tool": "shell",
      "params": {"command": "ls"}
    }
    """

    prompt = f"""
Você é um agente de sistema.
Objetivo: {task}

Ferramentas disponíveis:
{tools}

Escolha UMA ação no formato JSON:
{{"tool": "...", "params": {{}}}}
"""

    response = client_openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return eval(response.choices[0].message.content)
