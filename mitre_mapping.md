# MITRE ATT&CK Mapping — ClinicalShield AI

## Reference Table

All 12 attack vectors mapped to their target FHIR R4 resource and precise
MITRE ATT&CK sub-technique. Sub-techniques are used throughout (T1059.007
not T1059) for accurate ATT&CK Navigator heatmap generation.

| # | Attack Vector | FHIR Resource | Sub-Technique | Tactic | Severity |
|---|---|---|---|---|---|
| 1 | Prompt Injection | `MedicationRequest` | T1059.007 | Execution | Critical |
| 2 | JWT Token Forgery | All Resources | T1078.004 | Initial Access | Critical |
| 3 | FHIR Endpoint Enumeration | `CapabilityStatement` | T1083 | Discovery | High |
| 4 | SQL Injection via Query Params | `Patient` | T1190 | Initial Access | High |
| 5 | SSRF via Medication URLs | `MedicationRequest` | T1071.001 | Command & Control | High |
| 6 | Auth Bypass via Role Spoofing | `Practitioner` | T1078.004 | Privilege Escalation | High |
| 7 | IDOR on Patient IDs | `Patient` | T1083 | Discovery | High |
| 8 | HL7 Message Injection | `MessageHeader` | T1059 | Execution | Critical |
| 9 | Adversarial Clinical NLP Inputs | `DiagnosticReport` | T1565.001 | Impact | High |
| 10 | Verbose Error Leakage | `OperationOutcome` | T1592 | Reconnaissance | Medium |
| 11 | Unvalidated FHIR References | `Appointment` | T1071 | Command & Control | Medium |
| 12 | Timing Side-Channel | `Patient` / `Observation` | T1595.002 | Reconnaissance | Low |

---

## Detailed Notes

### T1059.007 — Command and Scripting Interpreter: JavaScript
**Vectors:** Prompt Injection (1), HL7 Message Injection (8)
Injecting commands into clinical text fields processed by AI models or
messaging workflows. In a FHIR context this targets free-text fields in
MedicationRequest.dosageInstruction.text and MessageHeader routing logic.

### T1078.004 — Valid Accounts: Cloud Accounts
**Vectors:** JWT Token Forgery (2), Auth Bypass via Role Spoofing (6)
Abusing the SMART on FHIR OAuth token system. T1078.004 applies because
FHIR authentication uses cloud-style bearer tokens. Forging or manipulating
JWT role claims (patient vs practitioner) falls under this sub-technique.

### T1083 — File and Directory Discovery
**Vectors:** FHIR Endpoint Enumeration (3), IDOR on Patient IDs (7)
Discovering available resources on the server. GET /metadata returns the
full CapabilityStatement. Sequential Patient IDs expose the full patient
list through simple enumeration.

### T1190 — Exploit Public-Facing Application
**Vectors:** SQL Injection (4)
Injecting malicious SQL via FHIR search query parameters targeting the
Patient resource. Example: GET /Patient?family=Smith' OR 1=1--

### T1071.001 — Application Layer Protocol: Web Protocols
**Vectors:** SSRF via Medication URLs (5)
MedicationRequest.medicationReference.url can point to an
attacker-controlled server. The FHIR server fetches it server-side,
enabling Server-Side Request Forgery.

### T1565.001 — Data Manipulation: Stored Data Manipulation
**Vectors:** Adversarial Clinical NLP Inputs (9)
Crafting clinical text in DiagnosticReport.conclusion that causes an AI
model to misclassify a diagnosis. Direct patient safety impact.

### T1592 — Gather Victim Host Information
**Vectors:** Verbose Error Leakage (10)
FHIR OperationOutcome responses on errors can leak stack traces, database
schema, and internal server paths if error handling is not configured.

### T1071 — Application Layer Protocol
**Vectors:** Unvalidated FHIR References (11)
Appointment.participant.actor references pointing to external attacker-
controlled URLs that the server fetches blindly to resolve the reference.

### T1595.002 — Active Scanning: Vulnerability Scanning
**Vectors:** Timing Side-Channel (12)
Response time differences between existing and non-existing Patient IDs
leak record existence without authentication. Patient/999 (exists) returns
in ~12ms. Patient/1000 (not found) returns in ~2ms.
