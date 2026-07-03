# ClinicalShield AI
An LLM-powered adversarial threat detection tool for FHIR R4 EHR systems

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://clinicalshield-ai.streamlit.app)

ClinicalShield AI simulates adversarial attacks against a mock FHIR R4 EHR API, classifies each attack using an LLM (Claude Haiku), maps findings to MITRE ATT&CK TTPs, and generates a clinical-grade threat assessment report.

🌐 [Live Dashboard](https://clinicalshield-ai.streamlit.app)

Enterprise healthcare systems are among the top 3 sectors targeted by ransomware globally. FHIR R4 is the standard for health data interoperability, mandated and adopted by Cerner, Heidi Health, and other emerging clinical AI platforms. With the rise of GenAI making sophisticated attacks easier to craft, and almost no purpose-built security tooling for FHIR-based clinical AI workflows, ClinicalShield AI aims to bridge that gap.

---

## What It Does

- Simulates 12 adversarial attack vectors against a mock FHIR R4 EHR API
- Classifies each request using Claude Haiku and maps findings to MITRE ATT&CK
- Visualises threat intelligence in an interactive Streamlit dashboard
- Generates a clinical-grade threat assessment report in PDF format
- Supports live attack simulation against a deployed FastAPI FHIR server

---

## System Architecture

```
User → Streamlit Dashboard → Attack Simulation Engine → FHIR Mock API (Railway)
                                                                ↓
                                                  LLM Threat Classifier (Claude Haiku)
                                                                ↓
                                                    MITRE ATT&CK Mapper
                                                                ↓
                                                  Report Generator → PDF Download
```

---

## Project Structure

```
clinicalshield-ai/
├── main.py               # Mock FHIR R4 server (FastAPI) — 5 endpoints
├── auth.py               # JWT authentication layer
├── app.py                # Streamlit dashboard (5 pages)
├── src/
│   ├── simulator.py      # Attack simulation engine
│   ├── classifier.py     # LLM threat classifier (Claude Haiku)
│   ├── mitre_mapper.py   # MITRE ATT&CK sub-technique mapping
│   └── report_generator.py
├── data/
│   └── attack_train.json # 946 labelled records (470 attacks, 476 benign)
├── results/
│   └── classifications.jsonl  # Pre-classified results for demo
├── classify_attacks.py   # Batch classifier for attack records
├── classify_benign.py    # Batch classifier for benign records
├── Procfile              # Railway deployment config
└── requirements.txt
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| EHR Mock API | FastAPI + Uvicorn |
| Attack Engine | Python + httpx |
| AI Classifier | Claude API (`claude-haiku-4-5-20251001`) |
| MITRE Mapping | ATT&CK TTP framework |
| Dashboard | Streamlit + Plotly |
| Report Export | fpdf2 |
| Deployment | Streamlit Cloud + Railway |

---

## Classifier Performance

| Metric | Score |
|--------|-------|
| Precision | 67.15% |
| Recall | 86.64% |
| F1 Score | 75.66% |
| Accuracy | 72.04% |

Recall is prioritised over precision — in clinical environments, a missed attack is far more costly than a false alarm.

---

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/yourname/clinicalshield-ai
cd clinicalshield-ai
pip install -r requirements.txt

# 2. Add your API key
echo "ANTHROPIC_API_KEY=your-key-here" > .env

# 3. Start the FHIR mock API
uvicorn main:app --reload

# 4. Launch the dashboard (new terminal)
streamlit run app.py
```

---

## Dataset

946 labelled FHIR R4 adversarial request-response pairs across 12 attack vectors and 37 FHIR resource types.

Schema: `attack_id | vector_type | fhir_resource | target_endpoint | http_method | payload | mitre_ttp | severity | is_attack`

---

## Attack Vectors Covered

`prompt_injection` · `sql_injection` · `jwt_token_forgery` · `role_spoofing` · `idor_patient_ids` · `fhir_endpoint_enumeration` · `ssrf_medication_url` · `hl7_message_injection` · `adversarial_nlp` · `verbose_error_leakage` · `unvalidated_fhir_reference` · `timing_side_channel`

---

## Disclaimer

This project uses a fully synthetic dataset and a mock API. No real patient data was used at any point. Built for security research and educational purposes only.
