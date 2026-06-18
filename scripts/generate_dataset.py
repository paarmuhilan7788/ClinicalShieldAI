import anthropic
import csv
import os
import json
from datetime import datetime

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

rows =[]#the list to hold the 17 rows based on the attack vector
with open("data/attack_dataset.csv", mode="r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

#group the rows by vector_type(eg:"prompt injetion" is one of th evector types, "jwt_token_forgery" is another)
categorized = {}
for row in rows:
    vtype = row["vector_type"]
    if vtype not in categorized:
        categorized[vtype] = []
    categorized[vtype].append(row)

gen_rows = []
count = 18 #seed rows terminate at ATK_017

for vtype, seed_rows in categorized.items():
    if vtype == "legitimate_request":
        continue

    seed = seed_rows[0]

    prompt = f"""You are generating synthetic cybersecurity attack data for a FHIR R4 healthcare API threat detection ML dataset.

    Here is an example attack row:
    {seed}

    Generate 12 more variations of the "{vtype}" attack type as a JSON array.
    Each object must have exactly these 12 fields:
    attack_id, vector_type, fhir_resource, target_endpoint, http_method, payload, expected_impact, mitre_ttp, mitre_tactic, owasp_llm, severity, is_attack

    Rules:
    - vector_type must stay exactly: {vtype}
    - is_attack must be: true
    - severity must be one of: critical, high, medium, low
    - Vary the payload creatively but keep it realistic
    - Return ONLY a valid JSON array, no explanation"""

    #Claude API Call
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=16000,
        messages=[{"role":"user", "content":prompt}]
    )

    #Parsing the response and passing them onto gen_rows[]
    content = response.content[0].text
    clean = content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    clean = clean.replace(": false", ": False").replace(": true", ": True").replace(": null", ": None")
    new_rows = eval(clean)

    for r in new_rows:
        r["attack_id"] = f"ATK_{count:03d}"
        r["generated_at"] = datetime.utcnow().isoformat()
        r["model_used"] = "claude-haiku-4-5-20251001"
        r["temperature"] = "default"
        count += 1
        gen_rows.append(r)

#Logic for legitimate requests
legit_seed = categorized["legitimate_request"][0]

legit_prompt = f"""Generate 30 legitimate (non-attack) FHIR R4 API request rows as a JSON array.

Example row:
{legit_seed}

Rules:
- vector_type must be: legitimate_request
- is_attack must be: false
- mitre_ttp, mitre_tactic, owasp_llm should be empty strings
- severity should be empty string
- Vary the endpoints and payloads realistically
- Return ONLY a valid JSON array, no explanation"""

legit_response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=16000,
    messages=[{"role": "user", "content": legit_prompt}]
)

legit_content = legit_response.content[0].text
legit_clean = legit_content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
legit_clean = legit_clean.replace(": false", ": False").replace(": true", ": True").replace(": null", ": None")
legit_rows = eval(legit_clean)

for r in legit_rows:
    r["attack_id"] = f"ATK_{count:03d}"
    r["generated_at"] = datetime.utcnow().isoformat()
    r["model_used"] = "claude-haiku-4-5-20251001"
    r["temperature"] ="default"
    count += 1
    gen_rows.append(r)

all_rows = rows + gen_rows
fieldnames = ["attack_id","vector_type","fhir_resource","target_endpoint","http_method","payload","expected_impact","mitre_ttp","mitre_tactic","owasp_llm","severity","is_attack","generated_at","model_used","temperature"]

with open("data/attack_dataset.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_rows)

print(f"Done. Total rows: {len(all_rows)}")

with open("data/attacks_v1.json", "w")as f:
    json.dump(all_rows, f, indent=2)
print(f"JSON data:data/attacks_v1.json")