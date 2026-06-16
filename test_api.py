#This file is to test the endpoints we built
#It returns any errors if present
#We use TestClient over here for testing purpose. Instead of opening a new browser and testing on it,
#we use this which is a fake browser. It lets Python pretned as a browser. 
from fastapi.testclient import TestClient
from main import app

#creating object for TestClient - fake browser
t_client = TestClient(app)

#1.Defining a helper function
def get_token():
   response =  t_client.post("/auth/token", json={
      "username" :"doctor_u",
      "password" :"doc123"
   })
   return response.json()["access_token"]

#2.403 on missing token
def test_missing_token():
   response = t_client.get("/fhir/r4/Patient/p001")
   assert response.status_code == 401

#3.200 on valid JWT
def test_valid_token():
   token = get_token()
   response = t_client.get("/fhir/r4/Patient/p001", headers={
      "Authorization" : "Bearer " + token
   })
   assert response.status_code == 200
   assert response.json()["id"] == "p001"

#4.200 on IDOR -----> GET Patient2 with Patient1's credentials
def test_idor_vuln():
   token = get_token()
   response = t_client.get("/fhir/r4/Patient/p002", headers={
      "Authorization" : "Bearer " + token
   })
   assert response.status_code == 200

#5.Metadata
def test_metadata():
   response = t_client.get("/fhir/r4/metadata")
   assert response.status_code == 200
   assert response.json()["resourceType"] == "CapabilityStatement"



