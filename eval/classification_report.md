# ClinicalShieldAI - LLm Classifier Evaluation Report

## LLM Model Used:
Claude Haiku (claude-haiku-4-5-20251001)

## Dataset
No.of evaluated records = 526
No.of attack records = 469
No.of legitimate records = 56

## Evaluation Metrics
Accuracy
|
64.95%
|
|
Precision
|
98.63%
|
|
Recall
|
61.26%
|
|
F1 Score
|
75.85%
|
## Baseline Comparison
|
Method
|
Accuracy
|
|
---------
|
---------
|
|
TF-IDF + Logistic Regression
|
94.81%
|
|
LLM Classifier - Claude
|
64.95%
|

## Key Observation
LLM Classifiers achieve 98.63% precision but only 61.26% recall on FHIR attack detction. This primarily revolves around the fact that LLM classifiers are highly dependent on the the response from the requests. It is trivial to note that minimal server responses provide insignificant data for the LLM to distinguish a real attack from a legitimate request. This is thus reflected on the recall score.

## Per-Class Breakdown
| Class | Precision | Recall | F1 |
|-------|-----------|--------|----|
| Legitimate (false) | 22% | 93% | 36% |
| Attack (true) | 99% | 62% | 76% |

## Root Cause Analysis
- Attacks returning 404 (endpoint not found) give Claude minimal response body context
- Claude defaults to classifying ambiguous cases as attacks — high precision, low recall
- FHIR endpoint enumeration and timing side-channel attacks are hardest to detect

## Critical Insight
It is of vital importance to realize that a response of 404 doesn't simply refer to a failed response. At the deeper level, it redirects this insight as an enumeration attack. 
For instance, 
Endpoint enumeration:

GET /fhir/r4/AllergyIntolerance returns 404 -request and response respectively
But the attacker now knows this endpoint doesn't exist — Reconnaisance
The primary motive of the attack is succeeded.

Thus, "Traditional response-based detection fails against reconnaissance attacks — a 404 is not evidence of no attack."

## Recommendations
1.Combine LLM classifier with rule-based pre-filter:
- If status_code == 404 AND payload contains sequential IDs → flag as IDOR attempt
- Use LLM for semantic analysis of response body content only when body is meaningful

2.Effective FHIR security monitoring must analyse **request patterns over time**, not individual 
responses in isolation.


