Threat Model — ClinicalShield AI

## Project Context

ClinicalShield AI simulates adversarial attacks against a mock FHIR R4 EHR API.
This threat model defines the attacker personas, entry points, goals, and
patient-safety impact used to design the 12 attack vectors in this project.

---

## Attacker Personas

### Persona 1 : External Ransomware Gang
| Field | Detail |
|-------|--------|
| **Who** | Organised cybercriminal group |
| **Motivation** | Financial - encrypt patient data, demand ransom |
| **Technical skill** | High - automated scanning, known exploit toolkits |
| **Access starting point** | Public-facing FHIR API endpoints |
| **Real-world example** | 2024 Change Healthcare breach, 2022 Medibank breach |

### Persona 2 : Malicious Insider
| Field | Detail |
|-------|--------|
| **Who** | Disgruntled employee or contractor with existing system access |
| **Motivation** | Data theft, sabotag, or selling patient records |
| **Technical skill** | Medium - knows internal systems and has valid credentials |
| **Access starting point** | Valid JWT token with Practitioner role |
| **Real-world example** | Insider accessing records of celebrities or family members |

---

## FHIR Attack Surface

These are the 8 FHIR R4 resource types exposed by the mock API and the sensitive data each one holds.

| FHIR Resource | Sensitive Data | If Compromised |
|---|---|---|
| `Patient` | Name, DOB, address, Medicare number | Identity theft, re-identification |
| `MedicationRequest` | Drug name, dosage, prescribing doctor | Dosage manipulation, AI poisoning |
| `Observation` | Lab results, vitals, test outcomes | Misdiagnosis if altered |
| `Appointment` | Scheduling, attendance, referrals | Workflow disruption |
| `DiagnosticReport` | Diagnosis text, clinical conclusions | AI misclassification if poisoned |
| `MessageHeader` | Routing metadata for clinical messages | Workflow hijacking |
| `OperationOutcome` | Server error details | Infrastructure reconnaissance |
| `CapabilityStatement` | Full list of server capabilities | Attack surface mapping |

---

## Entry Points

| Entry Point | Attack Vectors | Notes |
|---|---|---|
| `GET /Patient/{id}` | IDOR, SQL Injection, Timing Side-Channel | Sequential IDs make enumeration trivial |
| `POST /MedicationRequest` | Prompt Injection, SSRF | Clinical NLP processes free-text fields |
| `GET /Observation` | Adversarial NLP Inputs | AI model reads this data for diagnosis support |
| `POST /Appointment` | Unvalidated FHIR References | Server fetches actor reference URLs |
| `GET /metadata` | FHIR Endpoint Enumeration | Reveals full server capability to attacker |
| `JWT /auth/token` | JWT Token Forgery, Role Spoofing | Auth layer protecting all resources |

---

## Attacker Goals

| Goal | Attack Vectors Used | Likelihood |
|---|---|---|
| Exfiltrate patient records for sale | IDOR (7), SQL Injection (4) | High |
| Deploy ransomware via API foothold | Endpoint Enumeration (3), JWT Forgery (2) | High |
| Manipulate medication AI outputs | Prompt Injection (1), Adversarial NLP (9) | Medium |
| Escalate privileges from Patient to Practitioner | Role Spoofing (6) | Medium |
| Perform server-side reconnaissance | Error Leakage (10), Timing Side-Channel (12) | High |
| Hijack clinical messaging workflow | HL7 Message Injection (8) | Low |

---

## Patient Safety Impact

This is what makes healthcare breaches different from financial breaches —
the consequences are not just financial, they are clinical.

| Scenario | Impact |
|---|---|
| Prompt injection alters MedicationRequest dosage | Patient receives wrong medication dose |
| Adversarial input poisons DiagnosticReport AI | AI misclassifies a cancer diagnosis as benign |
| IDOR exposes all patient records | Mass identity theft, insurance fraud |
| JWT forgery grants Practitioner access | Attacker can create or modify clinical records |
| Ransomware via API foothold | Hospital systems go offline, surgeries delayed |

---

## Assumptions & Limitations

- This threat model is based on a **mock API** using synthetic Synthea data.
  No real patient data is involved at any point.
- The mock API intentionally has **no rate limiting** to allow simulation of
  high-volume attacks. A real EHR would have rate limiting as a control.
- JWT tokens in the mock API use a **weak shared secret** for testing purposes.
  Production systems use asymmetric keys (RS256).
- The threat model does not cover **physical access** or **social engineering**
  attack vectors — only API-level threats.

---

## Version

| Field | Detail |
|---|---|
| **Version** | 1.0 |
| **Date** | Day 1 of ClinicalShield AI build |
| **Author** | Paar Muhilan
