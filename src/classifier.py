#This is the LLM file(Claude) which will be predicting the is_attack and also the attack type(vector_type), the fhir resource
#being targted, the associated mitre_ttp and severity.
#Traditional baseline vs LLM

import anthropic
import json
import os

PROMPT = """
You are a clinical cybersecurity analyst for a healthcare organisation. 
Given an HTTP request-response pair from a FHIR R4 EHR system, respond ONLY with valid JSON:
{
    "is_attack": bool,
    "vector_type": string,
    "fhir_resource": string,
    "mitre_ttp": string,
    "mitre_tactic": string,
    "severity": "critical|high|medium|low",
    "confidence": float between 0 and 1,
    "explanation": "one sentence"
"""
class ThreatClassifier:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    def classify(self, payload, status_code, response_body, latency):
        userMesg = f"""Analyse this FHIR R4 API request-response pair:

Payload fired: {payload}
Status code: {status_code}
Response body: {response_body}
Latency (ms): {latency}

Respond ONLY with valid JSON."""
        
        response = self.client.messages.create(
            model = "claude-haiku-4-5-20251001",
            max_tokens=500,
            system = PROMPT,
            messages = [{"role" : "user", "content" : userMesg}]
        )

        content = response.content[0].text
        refined_content = content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(refined_content) 
    
#Defining the runner function
def runner_classifier():
    simulation_results = {}
    with open("results/simulation_results.jsonl", "r") as f:
        for line in f:
            record = json.loads(line)
            simulation_results[record["attack_id"]] = record #The key here is attack_id and the value is the entire row
    
    with open("data/attack_train.json", "r") as f:
        train_data = json.load(f)
    
    class1 = ThreatClassifier()

    with open("results/classifications.jsonl", "w") as o: #File to store Claude's prediction
        for record in train_data:
            attack_id = record["attack_id"] #Used to find the matching simulation result

            if attack_id not in simulation_results:
                continue
            sim = simulation_results[attack_id]
            try: #Claude API Call
                prediction = class1.classify(
                    payload=record["payload"],
                    status_code=sim["status_code"],
                    response_body=sim["response_body"],
                    latency=sim["latency_ms"]
                )
            except Exception as e:
                prediction = {"error": str(e)}

            result = {
                "attack_id": attack_id,
                "ground_truth": {
                    "is_attack": record["is_attack"],
                    "vector_type": record["vector_type"],
                    "fhir_resource": record["fhir_resource"],
                    "mitre_ttp": record["mitre_ttp"],
                    "severity": record["severity"]
                },
                "prediction": prediction
            }

            o.write(json.dumps(result) + "\n")
            print(f"Classified: {attack_id} | is_attack={prediction.get('is_attack')} | confidence={prediction.get('confidence')}")

if __name__ == "__main__":
    runner_classifier()




        
