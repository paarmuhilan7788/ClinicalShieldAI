#This file acts as the attacker. It takes the records from the dataset, fires the requests at the FastAPI server and returns the
#response in a log file. This log file is fed as the input for the LLM classifier where Claude predicts a legitimate req from an attack
import httpx
import asyncio
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

#To fire requests, we need a JWT token
def get_token():
    response = httpx.post(url=BASE_URL + "/auth/token", json={
        "username" : "doctor_u",
        "password" : "doc123"
    })
    return response.json()["access_token"]

def is_server_available():
    try:
        httpx.get(BASE_URL + "/health", timeout=2)
        return True
    except Exception:
        return False

class AttackSimulator:
    def __init__(self):
        if is_server_available():
            self.token = get_token()
            self.headers = {"Authorization" : "Bearer" + " " + self.token}
        else:
            self.token = None
            self.headers = {}

    def simulate(self, attack_record, mode="active"):
        endpoint = attack_record["target_endpoint"] #Where to deliver
        method = attack_record["http_method"]#How to deliver (the attack row)
        payload = attack_record["payload"]

        endpoint = endpoint.replace("{id}", "p001")

        url = BASE_URL + endpoint
        start = time.time()#records how long the attack takes place

        try:
            if method == "GET":
                response = httpx.get(url,headers=self.headers, timeout=5)
            elif method == "POST":
                response = httpx.post(url, headers=self.headers, timeout=5)
            else:
                response = httpx.get(url, headers=self.headers, timeout=5)

            latency = round((time.time() - start) * 1000, 2)
            return {
                "attack_id": attack_record["attack_id"],
                "vector_type": attack_record["vector_type"],
                "fhir_resource": attack_record["fhir_resource"],
                "mode": mode,
                "status_code": response.status_code,
                "latency_ms": latency,
                "response_body": response.text[:500],
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e1:
            return{
                "attack_id": attack_record["attack_id"],
                "vector_type": attack_record["vector_type"],
                "fhir_resource": attack_record["fhir_resource"],
                "mode": mode,
                "status_code": None,
                "latency_ms": None,
                "response_body": str(e1),
                "timestamp": datetime.utcnow().isoformat()
            }


def run_simulation_engine():
    with open("data/attack_train.json", "r") as f:
        records = json.load(f)

    sim = AttackSimulator() #instance of the AttackSimulator() class
    with open("results/simulation_results.jsonl", "w") as o:
        for record in records:
            result = sim.simulate(record, mode = "active")
            o.write(json.dumps(result) + "\n")
            print(f"Done: {result['attack_id']} | {result['status_code']} | {result['latency_ms']}ms")

if __name__ == "__main__":
    run_simulation_engine()

    



    