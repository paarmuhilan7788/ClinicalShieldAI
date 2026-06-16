# ClinicalShieldAI
An LLM powered threat detection tool for FHIR R4 Systems


![CI](https://github.com/yourname/clinicalshield-ai/actions/workflows/test.yml/badge.svg)
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

ClinicalShield AI simulates adversarial attacks against a mock FHIR R4 EHR API, classifies each attack using an LLM, maps findings to MITRE ATT&amp;CK TTPs and generates a clinical-grade threat assessment report. 

🎥 [Watch 3-minute Loom walkthrough](https://loom.com/your-link)  #to be changed
🌐 [Live Dashboard](https://your-app.streamlit.app) #to be changed

Enterprise healthcare systems are among the top 3 sectors targeted by ransomware globally. FHIR R4 is the standard for data interoperability, i.e data exchange among healthcare instituions and is mandated and adopted by Cerner, Heidi Health and other emerging AI scribes. As most of the security tooling is generic and withthe rise of GenAI, sphisticating an attack is much simpler these days. With almost no safepoint for FHIR based clinical AI workflows, this tool aims to thus bridge this necessity. 
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#WHAT THE PROJECT DOES?
-Simulates 12 different adversarial attacks against a mock FHIR R4 EHR API.
-Classifies each attack using Claude and maps the observation with MITRE ATT&CK
-Visualizes the findings in an interactive streamlist dashboard.
-Genrates a clinical grade threat assessment report in .pdf format. 

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#SYSTEM ARCHITECTURE

User → Streamlit Dashboard → Attack Simulation Engine → FHIR Mock API
↓
LLM Threat Classifier (Claude)
↓
MITRE ATT&CK Mapper
↓
Report Generator → PDF Download



PROJECT STRUCTURE:

clinicalshield-ai/
├── fhir_api/           # Mock FHIR R4 server (FastAPI)
│   └── main.py         # 5 endpoints including /metadata
├── src/
│   ├── simulator.py    # Attack simulation engine
│   ├── classifier.py   # LLM threat classifier (Claude)
│   └── mitre_mapper.py # MITRE ATT&CK sub-technique mapping
├── data/
│   ├── attacks_train.json   # 184 labelled attack records
│   ├── attacks_test.json    # 46 held-out test records
│   └── README.md            # Dataset schema documentation
├── results/            # Simulation + classification JSONL outputs
├── eval/               # Accuracy metrics + stress test results
├── reports/            # Generated PDF threat assessment reports
├── assets/             # Demo GIF, MITRE heatmap screenshot
├── research/           # Kaggle notebooks + references
├── outputs/            # ATT&CK Navigator layer JSON
├── tests/              # Unit + integration tests
├── app.py              # Streamlit dashboard (4 pages)
├── .env.example        # Environment variable template
└── docs/               # Threat model, journal, retrospective


-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
TECH STACK:

Layer | Technology |
|-------|------------|
| EHR Mock API | FastAPI + SQLite + Synthea Dataset |
| Attack Engine | Python + httpx + asyncio |
| AI Classifier | Claude API (`claude-sonnet-4-6`) |
| MITRE Mapping | STIX JSON + ATT&CK Navigator |
| Dashboard | Streamlit + Plotly |
| Report Export | fpdf2 |
| CI/CD | GitHub Actions |
| Deployment | Streamlit Cloud |

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/yourname/clinicalshield-ai
cd clinicalshield-ai
pip install -r requirements.txt

# 2. Add your API key
cp .env.example .env
# Open .env and add: ANTHROPIC_API_KEY=your-key-here

# 3. Start the FHIR mock API
uvicorn fhir_api.main:app --reload

# 4. Launch the dashboard (new terminal)
streamlit run app.py
```
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## Dataset

The 230-sample labelled FHIR adversarial attack dataset used in this project is publicly available on Kaggle:

📊 [FHIR R4 EHR Adversarial Attack Dataset](https://kaggle.com/yourname/fhir-attack-dataset)

Schema: `attack_id | vector_type | fhir_resource | target_endpoint | mitre_ttp | severity | is_attack`
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## Disclaimer

This project uses a fully synthetic dataset (Synthea) and a mock API.
No real patient data was used at any point. Built for security research and educational purposes only.

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Placeholders to add as I progress:

Kaggle link → Day 15 when you publish the dataset
Demo GIF → Day 16 when you record it
Live Streamlit URL → Day 17 when you deploy
Key Findings numbers → Day 6 after the classifier runs
Threat report PDF link → Day 14 when the report is done
Your name, email, LinkedIn → fill these in now actually
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Notes:
1.Anyone cloning the repository can generate the fhir.db just by running the load_synthea.py





