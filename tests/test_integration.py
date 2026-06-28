import json
import os
import pytest

VALID_FHIR_RESOURCES = [
    "Patient", "Observation", "MedicationRequest", "Appointment",
    "DiagnosticReport", "Condition", "Encounter", "Practitioner",
    "Organization", "AllergyIntolerance", "Immunization", "Procedure",
    "Device", "Location", "Medication", "Bundle", "MessageHeader",
    "CapabilityStatement", "OperationOutcome", "CarePlan", "CareTeam",
    "DocumentReference", "ServiceRequest", "Claim", "Goal",
    "Consent", "ClinicalImpression", "DeviceUseStatement", "FamilyMemberHistory",
    "MedicationAdministration", "MedicationDispense", "MedicationStatement",
    "NutritionOrder", "PractitionerRole", "ProcedureRequest", "Specimen",
    "Lab"
]

SIM_FILE = "results/simulation_results.jsonl"
CLASS_FILE = "results/classifications.jsonl"

#Test1 - To check the existence of the simulation_results file - empty or not
def test_simulation_results():
    if not os.path.exists(SIM_FILE):
        pytest.skip("simulation_results.jsonl not present in CI environment")
    assert os.path.getsize(SIM_FILE) > 0

#Test2 - To check the existence of the right and required records in the simulation_results file
def test_attributes_simulation():
    if not os.path.exists(SIM_FILE):
        pytest.skip("simulation_results.jsonl not present in CI environment")
    with open(SIM_FILE, "r") as f:
        lines = f.readlines()[:10]

    reqd_attributes = ["attack_id", "vector_type", "fhir_resource", "status_code", "latency_ms", "response_body"]

    for line in lines:
        rec = json.loads(line)
        for attri in reqd_attributes:
            assert attri in rec, f"Missing field {attri} in {rec.get('attack_id')}"

#Test3 - Validating the fhir_resource attribute - Whitelisting
def test_fhir_resource():
    if not os.path.exists(SIM_FILE):
        pytest.skip("simulation_results.jsonl not present in CI environment")
    with open(SIM_FILE, "r") as f:
        for line in f:
            rec = json.loads(line)
            fhir = rec.get("fhir_resource")
            assert fhir in VALID_FHIR_RESOURCES, f"Invalid fhir resource : {fhir} in {rec.get('attack_id')}"

#Test4 - Validating the existence and content of classifications.jsonl
def test_classifications():
    if not os.path.exists(CLASS_FILE):
        pytest.skip("classifications.jsonl not present in CI environment")
    assert os.path.getsize(CLASS_FILE) > 0

#Test 5 - To check if all records have an attackId
def test_no_null_attackID():
    if not os.path.exists(SIM_FILE):
        pytest.skip("simulation_results.jsonl not present in CI environment")
    with open(SIM_FILE, "r") as f:
        for line in f:
            rec = json.loads(line)
            id = rec.get("attack_id")
            assert id is not None and id != ""
