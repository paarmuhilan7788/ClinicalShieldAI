# ClinicalShield AI — Developer Journal

## What surprised me about FHIR resource types mapping to attack vectors?

The most surprising finding was that attack vectors don't map 1:1 to FHIR resources.
JWT Token Forgery and Role Spoofing both target the auth layer — but once successful,
they grant access to ALL resources simultaneously. A single forged JWT breaks the 
security of every endpoint at once.

Also surprising: the /metadata endpoint (CapabilityStatement) is the most dangerous
starting point for an attacker — it's public, requires no auth, and hands over the 
entire attack surface map in one request.

## Which FHIR resource has the largest attack surface?

**Patient** — targeted by 4 of the 12 attack vectors:
- SQL Injection (GET /Patient?name=...)
- IDOR (GET /Patient/{id})
- Timing Side-Channel (GET /Patient/9999)
- JWT Forgery (access any Patient record)

This makes sense — Patient is the most queried resource in any EHR system 
and contains the most sensitive PHI.

## What would I do differently?

1. Build the simulator with asyncio from Day 1 — sequential requests are too slow for 500+ records
2. Add fhir_resource whitelist to the LLM generator prompt — would have prevented 767 validation issues
3. Implement sliding window analysis for timing attacks — single-record classification fundamentally can't detect them

## Interview talking points

- "I discovered that LLM classifiers achieve high precision but low recall on FHIR attacks 
  — specifically because 404 responses give the model insufficient context"
- "The fhir_resource field is a novel evaluation dimension — most threat detection datasets 
  don't tie attacks to specific data model resources"
- "Timing side-channel attacks are architecturally undetectable by single-record classifiers 
  — they require sequence analysis across multiple requests"