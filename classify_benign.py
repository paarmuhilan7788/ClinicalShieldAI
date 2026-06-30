import json
import os
import sys
sys.path.append("src")

from simulator import AttackSimulator
from classifier import ThreatClassifier

simulator = AttackSimulator()
classifier = ThreatClassifier()

# Load only legitimate_request records
with open("data/attack_train.json") as f:
    data = json.load(f)

benign = [r for r in data if r["vector_type"] == "legitimate_request"]
print(f"Found {len(benign)} benign records to classify")

os.makedirs("results", exist_ok=True)

for i, record in enumerate(benign):
    try:
        simulator_result = simulator.simulate(record, mode="Active")
        pred = classifier.classify(
            payload=record["payload"],
            status_code=simulator_result["status_code"],
            response_body=simulator_result["response_body"],
            latency=simulator_result["latency_ms"],
            http_method=record.get("http_method"),
            endpoint=record.get("target_endpoint")
        )
        with open("results/classifications.jsonl", "a") as f:
            f.write(json.dumps({
                "attack_id": record["attack_id"],
                "ground_truth": {
                    "vector_type": record["vector_type"],
                    "fhir_resource": record["fhir_resource"],
                    "is_attack": False
                },
                "prediction": pred
            }) + "\n")

        print(f"[{i+1}/{len(benign)}] {record['attack_id']} — is_attack: {pred.get('is_attack')} | confidence: {pred.get('confidence')}")

    except Exception as e:
        print(f"[{i+1}/{len(benign)}] {record['attack_id']} failed: {e}")

print("\nDone. All benign records classified.")
