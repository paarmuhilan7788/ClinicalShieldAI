##Day2 starts with building the FASTAPI Server. 

#Importing the dependencies
from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel
from datetime import datetime
import uuid

#FastAPI instance creation
app = FastAPI(
    title="ClinicalShield AI - Mock FHIR R4 API",
    version="1.0.0"
)

#Mock Patients-ResourceType data
patients = {
    "p001" : {"id":"p001", "resourceType":"Patient", "name":"Tom", "gender":"M", "birthDate":"1985-03-12"},
    "p002" : {"id":"p002", "resourceType":"Patient", "name":"Jessica", "gender":"F", "birthDate":"1993-05-19"},
    "p003" : {"id":"p003", "resourceType":"Patient", "name":"Maaran", "gender":"M", "birthDate":"1959-02-08"}
}

#This list will hold the data for the entries given via the second endpoint
medications = []
#SEED Data for Endpoint3 ------> Observations
observations = [
    {
        "id":"obs-001",
        "resourceType":"Observation",
        "status":"final",
        "subject":{"reference":"Patient/p003"},
        "code":{"text":"Body Weight"}
    },

    {
        "id":"obs-002",
        "resourceType":"Observation",
        "status":"final",
        "subject":{"reference":"Patient/p001"},
        "code":{"text":"Blood Pressure"},
    },

    {
        "id":"obs-003",
        "resourceType":"Observation",
        "status":"final",
        "subject":{"reference":"Patient/p002"},
        "code":{"text":"Oxygen Saturation"},
    },

    {
        "id":"obs-004",
        "resourceType":"Observation",
        "status":"final",
        "subject":{"reference":"Patient/p003"},
        "code":{"text":"Blood Glucose"},
    },

    {
        "id":"obs-005",
        "resourceType":"Observation",
        "status":"final",
        "subject":{"reference":"Patient/p001"},
        "code":{"text":"Heart Rate"}
    }
]

#Appointments list is for Endpoint 4
appointments = []

#MedicationRequest class for Endpoint2
#This informs FastAPI that when a client posts to this endpoint, this is what is to expect
class MedicationRequest(BaseModel):
    drug:str
    patientID:str 
    dosage:str


#Seed Data - Pydantic Model for Endpoint 4
#Pydantic model auto-validates the input data for type conversion or serialization
class AppointmentBody(BaseModel):
    patientId : str
    date : str
    reason : str



##Endpoint1 GET /fhir/r4/Patient/{id}
@app.get("/fhir/r4/Patient/{id}",status_code=200)#decorator for FastAPI
def get_patient(id:str):
    if id in patients:
        return patients[id]
    raise HTTPException(status_code=404, detail="No records found :(")

##Endpoint 2 POST /fhir/r4/MedicationRequest
@app.post("/fhir/r4/MedicationRequest",status_code=201)
def add_medication(body:MedicationRequest):
    new_record={
        "id":"med-"+str(uuid.uuid4())[:8],
        "resourceType":"MedicationRequest",
        "status":"active",
        "subject":{"reference":"Patient/"+body.patientID},
        "medicationCodeableConcept": {"text": body.drug},
        "dosageInstruction":[{"text":body.dosage}],
        "authoredOn":datetime.now().isoformat()
    }
    medications.append(new_record)
    return new_record

#Endpoint 3 GET /fhir/r4/Observation
@app.get("/fhir/r4/Observation")
def get_observation(subject:str=None):#FastAPI validates the parse automatically and checks for ?subject. If present, it returns only that from the list or else the whole in a bundle
    #looping is to be done through the observations list----->object is required
    if subject:
        filteredData = [obs for obs in observations if obs["subject"]["reference"]==subject]
    else:
        filteredData = observations

    return{
        "resourceType":"Bundle",
        "type":"searchset",
        "total":len(filteredData),
        "entry": [{"resource":obs}for obs in filteredData]
    }


#Endpoint 4
@app.post("/fhir/r4/Appointment", status_code=201)
def add_appointment(body: AppointmentBody):
    new_record = {
        "id":"appt-"+str(uuid.uuid4())[:8],
        "resourceType":"Appointment",
        "status":"booked",
        "start":body.date,
        "reasonCode":[{"text":body.reason}],
        "participant":[{"actor": {"reference": "Patient/" + body.patientId}}]
    }
    appointments.append(new_record)
    return new_record

#Endpoint 5 - Attack vector 3: FHIR Endpoint Enumeration
@app.get("/fhir/r4/metadata")
def fetch_metadata():
    return {
        "resourceType":"CapabilityStatement",
        "status":"active",
        "fhirVersion":"4.0.1",
        "kind":"instance",
        "rest":
        [
            {
            "mode":"server",
            "resource":
            [
                {
                    "type":"Patient",
                    "interaction":[{"code": "read"}, {"code": "search-type"}]
                },
                {
                    "type":"Observation",
                    "interaction":[{"code": "read"}, {"code": "search-type"}]
                },
                {
                    "type":"MedicationRequest",
                    "interaction": [{"code": "read"}, {"code": "create"}]
                },
                {
                    "type": "Appointment",
                    "interaction": [{"code": "read"}, {"code": "create"}]
                },
                {
                    "type": "DiagnosticReport",
                    "interaction": [{"code": "read"}, {"code": "search-type"}]
                }
            ]}

        ]
    }
    

    
