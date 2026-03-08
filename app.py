from flask import Flask, request, render_template
import os
from dotenv import load_dotenv
from groq import Groq
import markdown

load_dotenv()

app = Flask(__name__)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are a friendly brand naming assistant helping small business owners.
Use simple language and short sentences.
"""

USER_PROMPT_TEMPLATE = """
Business description: {business}

Proposed brand name: {name}

Please do the following:

1. Rate the name from 1–10 for:
   - Clarity
   - Memorability
   - Emotional Appeal

2. List 3–5 pros.

3. List 3–5 cons or weaknesses.

4. Suggest 3–5 alternative brand names.

Use clear headings like:
Ratings
Pros
Cons
Alternative Names
"""

def parse_ai_result(ai_text):
    sections = {
        "ratings": [],
        "pros": [],
        "cons": [],
        "alternatives": []
    }

    current = None
    ai_text = ai_text.replace("•", "-")

    for line in ai_text.splitlines():
        line = line.strip()

        if not line:
            continue

        lower = line.lower()

        if "ratings" in lower:
            current = "ratings"
            continue
        elif "pros" in lower:
            current = "pros"
            continue
        elif "cons" in lower or "weakness" in lower:
            current = "cons"
            continue
        elif "alternative" in lower:
            current = "alternatives"
            continue

        if current:
            if line.startswith("-"):
                line = line[1:].strip()

            sections[current].append(markdown.markdown(line))

    return sections


@app.route("/", methods=["GET", "POST"])
def index():

    result = None

    if request.method == "POST":

        brand_name = request.form["brand_name"]
        business_desc = request.form["business_desc"]

        prompt = USER_PROMPT_TEMPLATE.format(
            business=business_desc,
            name=brand_name
        )

        try:

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
            )

            ai_text = response.choices[0].message.content

            result = parse_ai_result(ai_text)

        except Exception as e:
            result = {"error": str(e)}

    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)