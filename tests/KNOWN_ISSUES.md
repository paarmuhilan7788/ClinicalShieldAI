# Known Issues — ClinicalShield AI

## Issue 1: LLM Misclassifies 404 Responses as Legitimate
**Affected vectors:** IDOR, Endpoint Enumeration, Timing Side-Channel  
**Root cause:** When the FHIR server returns `{"detail": "Not Found"}`, Claude has insufficient 
context to determine if the request was malicious or a legitimate miss.  
**Impact:** Recall drops to 61.62% — 38% of real attacks missed.  
**Fix:** Add rule-based pre-filter for 404 responses with sequential ID patterns.  
**Status:** Open

## Issue 2: vector_type Naming Mismatch
**Affected vectors:** All  
**Root cause:** Claude uses descriptive names ("JWT Algorithm Manipulation") instead of our 
exact snake_case labels ("jwt_token_forgery").  
**Impact:** vector_type prediction accuracy is low despite correct attack identification.  
**Fix:** Add vector_type enum to system prompt and instruct Claude to use exact labels only.  
**Status:** Open

## Issue 3: Timing Side-Channel Indistinguishable from Normal Traffic
**Affected vectors:** timing_side_channel (ATK_012)  
**Root cause:** A timing attack looks identical to a legitimate GET /Patient/{id} request. 
The only difference is the pattern across multiple requests — not detectable in a single record.  
**Impact:** Single-record classifier cannot detect timing attacks by design.  
**Fix:** Implement sliding window analysis across request sequences.  
**Status:** By design — requires architectural change beyond Day 7 scope.

## Issue 4: Claude's usage of it's non-standard fhir_resource values
**Affected** All records returning a response of 404
**Root cause** Claude sets it's own terminologies like "Unknown (404)", "N/A","Bundle (Observation)" instead of exact FHIR R4 resource type names.
**Impact** 767 validation issues across 526 records
**Resolution** include specifics in the system prompt.

## Issue 5: Invalid fhir_resource
**Affected** ATK_120
**Root-Cause** LLM has generated non standard fhir values
**Impact:** Integration test fails on fhir_resource whitelist assertion  
**Fix:** Re-run generator with explicit fhir_resource whitelist in prompt  
**Status:** Open