from openai import OpenAI
import os
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


SYSTEM_PROMPT = """
You are an internal IT service operations analyst.

You are NOT responsible for grouping or clustering incidents.
The incidents provided to you have already been grouped by semantic similarity.

Your task is to analyse the group and explain patterns based strictly on
the information provided.

Rules:
- Do not re-group or reclassify incidents
- Do not invent facts not supported by the data
- If evidence is insufficient, say so explicitly
- Hypotheses must be labelled as hypotheses
- Be concise and technically accurate
"""


def analyse_group(descriptions: list[str]) -> dict:
    user_prompt = f"""
Below is a group of incident descriptions that are semantically similar.

Please provide the following in JSON format:

1. group_label
2. summary
3. common_patterns
4. hypotheses
5. recommended_checks

Incident descriptions:
"""

    for d in descriptions:
        user_prompt += f"- {d}\n"

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2
    )

    content = response.choices[0].message.content.strip()

    # Remove Markdown code fences if present
    if content.startswith("```"):
        content = content.strip("`")
        content = content.replace("json", "", 1).strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "error": "Failed to parse LLM response",
            "raw_response": content
        }

