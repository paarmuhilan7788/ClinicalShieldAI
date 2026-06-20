import json
import re
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s :%(message)s")

VALID_SEVERITY = ["critical", "high", "medium", "low"]

VALID_FHIR_RES = ["Patient", "Observation", "MedicationRequest", "Appointment",
    "DiagnosticReport", "Condition", "Encounter", "Practitioner",
    "Organization", "AllergyIntolerance", "Immunization", "Procedure",
    "Device", "Location", "Medication", "Bundle", "MessageHeader",
    "CapabilityStatement", "OperationOutcome", "CarePlan", "CareTeam"]

MITRE_PATTERN = re.compile(r"^T\d{4}(\.\d{3})?$")

def record_validation(record, source): #validate_record ; record--->pred, source--->fPath [mapping with the validate_file function]
    issues_count = 0

    fhir = record.get("fhir")
    if not fhir or fhir not in VALID_FHIR_RES:
        logging.warning(f"[{source}] Invalid fhir_resource : {fhir} in {record.get('attack_id')}")
        issues_count += 1

    mitre_id = record.get("mitre_ttp")
    if mitre_id and not MITRE_PATTERN.match(mitre_id):
        logging.warning(f"[{source}] Invalid mitre_ttp format :{mitre_id} in {record.get('attack_id')}")
        issues_count += 1
    
    sev = record.get("severity")
    if sev and sev not in VALID_SEVERITY:
        logging.warning(f"[{sev}] Invalid severity : {sev} in {record.get('attack_id')}")
        issues_count += 1
    
    confidence = record.get("confidence")
    if confidence is not None and not (0 <= float(confidence) <= 1):
        logging.warning(f"[{source}] Invalid confidence: {confidence} in {record.get('attack_id')}")
        issues_count += 1

   # logging.debug(f"fhir={fhir}, mitre={mitre_id}, severity={sev}, confidence={confidence}")
    return issues_count

def validate_file(fPath):
    total_issues = 0
    total_count = 0

    with open(fPath, "r") as f:
        for line in f:
            record = json.loads(line)
        
            #for classification.jsonl file, we need to validate the prediction block
            if "prediction" in record:
                pred = record.get("prediction", {})
                if "error" not in pred:
                    total_issues +=  record_validation(pred, fPath)
                else:
                    total_issues +=  record_validation(record, fPath)
            
            total_count += 1

    logging.info(f"{fPath}: {total_count} records checked, {total_issues} issues found")
    return total_issues

if __name__ == "__main__":
    validate_file("results/simulation_results.jsonl")
    validate_file("results/classifications.jsonl") 
