import json
import os

# Step 2 - Load MITRE STIX data and build lookup dict
def load_mitre_stix():
    with open("data/enterprise-attack.json", "r") as f:
        stix_data = json.load(f)
    
    lookup = {}
    for obj in stix_data["objects"]:
        if obj.get("type") != "attack-pattern":#only technique and sub-technique matter in this context - attack pattern is the conventional name for these.
            continue
        
        # Extract TTP ID
        ttp_id = None
        for ref in obj.get("external_references", []):
            if ref.get("source_name") == "mitre-attack":
                ttp_id = ref.get("external_id")
                break
        
        if not ttp_id:
            continue

        # Extract tactic
        tactics = [p["phase_name"] for p in obj.get("kill_chain_phases", [])]
        
        lookup[ttp_id] = {
            "name": obj.get("name"),
            "tactic": tactics[0] if tactics else "unknown"
        }
    
    return lookup

ATTACK_MAPPING = {
    "prompt_injection":           {"ttp": "T1059.007", "fhir_resource": "MedicationRequest", "tactic": "Execution"},
    "jwt_token_forgery":          {"ttp": "T1078.004", "fhir_resource": "Patient", "tactic": "Initial Access"},
    "fhir_endpoint_enumeration":  {"ttp": "T1083",     "fhir_resource": "CapabilityStatement", "tactic": "Discovery"},
    "sql_injection":              {"ttp": "T1190",     "fhir_resource": "Patient", "tactic": "Initial Access"},
    "ssrf_medication_url":        {"ttp": "T1071.001", "fhir_resource": "MedicationRequest", "tactic": "Command and Control"},
    "role_spoofing":              {"ttp": "T1078.004", "fhir_resource": "Practitioner", "tactic": "Privilege Escalation"},
    "idor_patient_ids":           {"ttp": "T1083",     "fhir_resource": "Patient", "tactic": "Discovery"},
    "hl7_message_injection":      {"ttp": "T1059",     "fhir_resource": "MessageHeader", "tactic": "Execution"},
    "adversarial_nlp":            {"ttp": "T1565.001", "fhir_resource": "DiagnosticReport", "tactic": "Impact"},
    "verbose_error_leakage":      {"ttp": "T1592",     "fhir_resource": "OperationOutcome", "tactic": "Reconnaissance"},
    "unvalidated_fhir_reference": {"ttp": "T1071",     "fhir_resource": "Appointment", "tactic": "Command and Control"},
    "timing_side_channel":        {"ttp": "T1595.002", "fhir_resource": "Patient", "tactic": "Reconnaissance"},
    "legitimate_request":         {"ttp": "",          "fhir_resource": "", "tactic": ""}
}

def load_classifications():
    mitre_lookup = load_mitre_stix()
    enriched = []

    with open("results/classifications.jsonl", "r") as f:
        for line in f:
            record = json.loads(line)
            
            vector_type = record.get("ground_truth", {}).get("vector_type", "")
            mapping = ATTACK_MAPPING.get(vector_type, {})
            ttp_id = mapping.get("ttp", "")
            
            # Enrich with MITRE name from STIX lookup
            mitre_info = mitre_lookup.get(ttp_id, {})
            
            record["mitre_enriched"] = {
                "ttp_id": ttp_id,
                "ttp_name": mitre_info.get("name", "Unknown"),
                "tactic": mapping.get("tactic", ""),
                "fhir_resource": mapping.get("fhir_resource", "")
            }
            
            enriched.append(record)

    with open("outputs/classified_with_mitre.jsonl", "w") as f:
        for record in enriched:
            f.write(json.dumps(record) + "\n")

    print(f"Enriched {len(enriched)} records → outputs/classified_with_mitre.jsonl")
    return enriched

def generate_navigator_layer(enriched):
    print(f"Enriched count :{len(enriched)}")
    # Count frequency of each TTP
    ttp_counts = {}
    for record in enriched:
        ttp_id = record.get("mitre_enriched", {}).get("ttp_id", "")
        print(f"ttp_id found: {ttp_id}")
        fhir = record.get("mitre_enriched", {}).get("fhir_resource", "")
        if ttp_id:
            if ttp_id not in ttp_counts:
                ttp_counts[ttp_id] = {"count": 0, "fhir_resource": fhir}
            ttp_counts[ttp_id]["count"] += 1

    # Build Navigator layer
    techniques = []
    for ttp_id, data in ttp_counts.items():
        techniques.append({
            "techniqueID": ttp_id,
            "score": data["count"],
            "color": "",
            "comment": f"FHIR Resource: {data['fhir_resource']}",
            "enabled": True
        })

    layer = {
        "name": "ClinicalShield AI — FHIR Attack Coverage",
        "versions": {"attack": "14", "navigator": "4.9.1", "layer": "4.5"},
        "domain": "enterprise-attack",
        "description": "Attack frequency by technique — ClinicalShield AI simulation",
        "techniques": techniques,
        "gradient": {
            "colors": ["#ffffff", "#ff0000"],
            "minValue": 0,
            "maxValue": max(d["count"] for d in ttp_counts.values()) if ttp_counts else 1
        }
    }

    os.makedirs("outputs", exist_ok=True)
    with open("outputs/attack_navigator_layer.json", "w") as f:
        json.dump(layer, f, indent=2)

    print(f"Navigator layer saved → outputs/attack_navigator_layer.json")

    return layer

if __name__ == "__main__":
    enriched = load_classifications()
    generate_navigator_layer(enriched)