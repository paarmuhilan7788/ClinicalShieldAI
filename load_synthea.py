#loader file for iterating through a DB holding the tables for the resources
import sqlite3
import json
import os


#Paths
db_path = "fhir.db"
synthea_folder = "synthea_data"

#Connecting to sqlite3 database
conn = sqlite3.connect(db_path)#creating an instance for sqlite3 class and using the .connect method to connect it
cursor = conn.cursor()#for looping and iteration

#Creating the tables

#Table for Patients
cursor.execute("""
               CREATE TABLE IF NOT EXISTS Patients (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    birthDate TEXT,
                    gender TEXT
               
               )             
        """)

#Table for Observations
cursor.execute("""
               CREATE TABLE IF NOT EXISTS Observations (
                    id TEXT PRIMARY KEY,
                    status TEXT,
                    subject TEXT,
                    code TEXT
               )    
               """)

#Table for MedicationRequests
cursor.execute("""
                CREATE TABLE IF NOT EXISTS MedicationRequests(
                    id TEXT PRIMARY KEY,
                    status TEXT,
                    subject TEXT,
                    medication TEXT,
                    authoredOn TEXT
               )              
               """)

#counters
patients_count = 0
observations_count = 0
medications_count = 0

#looping over every file in the synthea folder
for f_name in os.listdir(synthea_folder):
    #if the file's name starts with hospital or practitioner then skip the file
    if f_name.startswith("hospital") or f_name.startswith("practitioner"):
        #skip
        continue

    #Building the full path
    filePath = os.path.join(synthea_folder, f_name)
    try:
        with open(filePath, "r", encoding="utf-8") as f:#open the file in read mode
            bundle = json.load(f)#load the file as a python dictionary into 'bundle'

        #Loop through every entry in the bundle
        for e in bundle.get("entry", []):
            resource = e.get("resource", {})
            resource_type = resource.get("resourceType","")

        #PATIENT
            if resource_type=="Patient":
                pid = resource.get("id","")
                gender = resource.get("gender","nil")
                birthDate = resource.get("birthDate","")
                nameObject = resource.get("name",[{}])[0]
                given = nameObject.get("given", [""])[0]
                family = nameObject.get("family", "")
                name = given + " " + family

                cursor.execute("""
                            INSERT OR IGNORE INTO Patients (id, name, gender, birthDate)
                            VALUES (?, ?, ?, ?)
                            """, (pid, name, gender,birthDate ))
                patients_count += 1

            #OBSERVATION
            elif resource_type == "Observation":
                #the variables in the left are the names according to our comfort
                oid = resource.get("id", "")
                status = resource.get("status","")
                subject = resource.get("subject",{}).get("reference","")#subject is a nested dictionary
                code = resource.get("code",{}).get("text","nil")

                cursor.execute("""
                    INSERT OR IGNORE INTO Observations (id, status, subject,code)
                            VALUES (?, ?, ?, ?)
                            """, (oid, status, subject, code))
                
                observations_count +=1

            #MEDICATION REQUESTS
            elif resource_type == "MedicationRequest":
                mid = resource.get("id", "")
                status = resource.get("status","nil")
                authoredOn = resource.get("authoredOn","")
                subject = resource.get("subject",{}).get("reference","")
                medCodeConcept = resource.get("medicationCodeableConcept",{}).get("text","")

                cursor.execute("""
                    INSERT OR IGNORE INTO MedicationRequests (id,status, authoredOn, subject, medication)
                            VALUES(?, ?, ?, ?, ?)
                            """,(mid, status, authoredOn, subject, medCodeConcept))
                
                medications_count += 1
    
    except Exception as ME:
        print(f"Dodging {f_name}:{ME}")
        continue

conn.commit()
conn.close()

#Printing the summary
print(f"Patients observed : {patients_count}")
print(f"Observations uploaded : {observations_count}")
print(f"Medications uploaded : {medications_count}")
print(f"Database stored at {db_path}")



            



            
