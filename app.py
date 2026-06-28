#Streamlit - python library that turns python code into interactive web pages
#port 8501

import streamlit as st
import pandas as pd
import os
import json
import sys
import base64
import plotly.express as px


sys.path.append("src") #when importing modules, look up the src folder
from simulator import AttackSimulator
from classifier import ThreatClassifier

st.set_page_config(
    page_title = "ClinicalShieldAI",
    page_icon= "🛡️",
    layout = "wide"
)

def get_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

img = get_base64(os.path.join(os.path.dirname(__file__), "assets", "heart.jpg"))

#Page config and dark theme CSS
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Exo+2:wght@300;400;600;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

st.markdown(f"""
<style>
    .main {{ background-color: #0e1117; }}
    html, body, [class*="css"], * {{ font-family: 'Exo 2', sans-serif !important; }}
    .block-container {{ padding-top: 8rem !important; }}
    .stButton>button {{ background-color: #ff4b4b; color: white; border-radius: 8px; }}
    .stSelectbox {{ background-color: #1e2130; }}
    .metric-card {{ background-color: #1e2130; padding: 1rem; border-radius: 8px; border-left: 4px solid #ff4b4b; }}
    html, body, [class*="css"] {{ font-size: 22px !important; -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-rendering: optimizeLegibility; }}
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpeg;base64,{img}");
        background-size: 35%;
        background-position: center center;
        background-attachment: fixed;
        background-repeat: no-repeat;
        image-rendering: crisp-edges;
    }}
    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.55);
    }}
</style>
""", unsafe_allow_html=True)

#Side-Navigation_Bar
with st.sidebar:
    st.title("ClinicalShieldAI"),
    st.caption("LLM Powerd FHIR Threat Detection"),
    st.divider()#horizontal divider

#Metadata
m1, m2, m3 = st.columns(3)
m1.markdown("**Model:** claude-haiku-4-5-20251001")
m2.markdown("**FHIR Version:** R4")
m3.markdown("**Attack Vectors:** 12")

if "total_attacks" not in st.session_state:#session_state is Streamlit's sort of memory buffer
    st.session_state.total_attacks = 0

st.metric("Total Attacks This Session", st.session_state.total_attacks)

if st.button("Reset Session"):# Reset button ----> counter=0, returns app to refresh
    st.session_state.total_attacks = 0
    st.rerun()


#PAGE NAVIGATION
page = st.sidebar.selectbox(
    "Navigation",
    ["Live Simulation", "Threat Classifications", "MITRE Heatmap", "Generate Report"]
)

if page == "Live Simulation":
    st.title("⚔️ Live Attack Simulation")
    st.caption("Fire real attack payloads against the FHIR R4 mock API")

    col1, col2, col3 = st.columns(3) #Defines three columns

    with col1:
        vector_type = st.selectbox("Attack Vector", ["prompt_injection", "jwt_token_forgery", "fhir_endpoint_enumeration",
            "sql_injection", "ssrf_medication_url", "role_spoofing",
            "idor_patient_ids", "hl7_message_injection", "adversarial_nlp",
            "verbose_error_leakage", "unvalidated_fhir_reference", "timing_side_channel"])
        
    with col2:
        fhir_filter = st.selectbox("FHIR Resource Selection", ["All", "Patient", "MedicationRequest", "Observation",
            "Appointment", "DiagnosticReport", "Practitioner",
            "CapabilityStatement", "MessageHeader"])
        
    with col3:
        attack_counter = st.slider("Number of Attacks", min_value=1, max_value=50, value=5)

    if st.button("Run Attack Simulation"):
        with open("data/attack_train.json", "r") as r:
            all_records = json.load(r)


        #Filtering the result to be sent based on user choices
        filtered = [rec for rec in all_records if rec["vector_type"] == vector_type]#Matches the value from vector_type
        if fhir_filter != "All":
            filtered = [rec for rec in filtered if rec["fhir_resource"] == fhir_filter]#Matches the value from fhir_filter

        filtered = filtered[:attack_counter]
        if not filtered:
            st.warning("No records found for the selection!Shoot your shot with other filters")
        
        else:
            simulator = AttackSimulator()
            classifier = ThreatClassifier()
            results =[]

            with st.status("Running simulation...") as status:
                for i, record in enumerate(filtered): #enumerate assigns both index and the record itself
                    simulator_result = simulator.simulate(record, mode = "Active")
                    pred = classifier.classify(
                        payload=record["payload"],
                        status_code=simulator_result["status_code"],
                        response_body=simulator_result["response_body"],
                        latency=simulator_result["latency_ms"]
                    )
                    results.append({
                        "attack_id": record["attack_id"],
                        "vector_type": record["vector_type"],
                        "fhir_resource": record["fhir_resource"],
                        "status_code": simulator_result["status_code"],
                        "latency_ms": simulator_result["latency_ms"],
                        "is_attack": pred.get("is_attack"),
                        "severity": pred.get("severity"),
                        "confidence": pred.get("confidence"),
                        "explanation": pred.get("explanation")
                    })

                    with open("results/classifications.jsonl", "a") as f:
                        f.write(json.dumps({
                            "attack_id": record["attack_id"],
                            "ground_truth": {"vector_type": record["vector_type"], "fhir_resource": record["fhir_resource"]},
                            "prediction": pred
                        }) + "\n")

                    st.session_state.total_attacks += 1
                    status.update(label=f"Processed {i+1}/{len(filtered)} attacks...")

            st.success(f"Simulation complete — {len(results)} attacks processed")
            #st.dataframe(pd.DataFrame(results), use_container_width=True)
            st.success(f"Simulation complete — {len(results)} attacks processed")

            for r in results:
                severity_color = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(r.get("severity"), "⚪")
                is_attack_label = "⚠️ ATTACK" if r.get("is_attack") else "✅ BENIGN"
    
                with st.container():
                    st.markdown(f"""
                    <div style="background-color:#1e2130; padding:1rem; border-radius:8px; margin-bottom:0.75rem; border-left:4px solid {'#ff4b4b' if r.get('is_attack') else '#00cc88'}">
                        <div style="display:flex; justify-content:space-between; align-items:center">
                            <span style="font-weight:bold; color:white">{r['attack_id']} — {r['vector_type']}</span>
                            <span style="color:{'#ff4b4b' if r.get('is_attack') else '#00cc88'}; font-weight:bold">{is_attack_label}</span>
                        </div>
                        <div style="color:#aaa; font-size:0.85rem; margin-top:0.5rem">
                            {severity_color} Severity: <b style="color:white">{r.get('severity','—')}</b> &nbsp;|&nbsp;
                            🎯 Resource: <b style="color:white">{r['fhir_resource']}</b> &nbsp;|&nbsp;
                            📡 Status: <b style="color:white">{r.get('status_code','—')}</b> &nbsp;|&nbsp;
                            ⏱ Latency: <b style="color:white">{r.get('latency_ms','—')}ms</b> &nbsp;|&nbsp;
                            🎲 Confidence: <b style="color:white">{r.get('confidence','—')}</b>
                        </div>
                        <div style="color:#ccc; font-size:0.85rem; margin-top:0.5rem">💬 {r.get('explanation','—')}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    


elif page == "Threat Classifications":
    st.title("🔍 Threat Classifications")
    st.caption("Browse and filter all LLM-classified attack results")

    try:
        records =[]
        with open("results/classifications.jsonl" ,"r") as f:
            for line in f:
                rec = json.loads(line)
                records.append(rec)
        
        df = pd.DataFrame(records)#analyzes the classification.jsonl file and converts every key into a column header

        df["is_attack"] = df["prediction"].apply(lambda x: x.get("is_attack", False))
        df["severity"] = df["prediction"].apply(lambda x: x.get("severity", ""))
        df["vector_type"] = df["prediction"].apply(lambda x: x.get("vector_type", ""))
        df["explanation"] = df["prediction"].apply(lambda x: x.get("explanation", ""))

        col1, col2 = st.columns(2)
        with col1:
            sev_filter = st.multiselect("Filter by Severity", ["critical", "high", "medium", "low"], default=["critical", "high", "medium", "low"])
        with col2:
            attack_only = st.checkbox("Show attacks only", value=True)

        if attack_only:
            df = df[df["is_attack"] == True]
        
        df = df[df["severity"].isin(sev_filter)]

        st.metric("Records shown", len(df))
        display_df = pd.DataFrame({
        "Attack ID": df["attack_id"] if "attack_id" in df.columns else df.index,
        "Is Attack": df["is_attack"],
        "Severity": df["severity"],
        "Vector Type": df["vector_type"],
        "Explanation": df["explanation"]
})
        st.dataframe(display_df, use_container_width=True)

    except FileNotFoundError:
        st.warning("No classifications found. Run a simulation first.") 



elif page == "MITRE Heatmap":
    st.title("🗺️ MITRE ATT&CK Heatmap")

    try:
        from mitre_mapper import load_classifications, generate_navigator_layer

        records = load_classifications()
        #st.write(records[0])

        if not records:
            st.warning("No classifications found. Run a simulation first.")
        else:
            df = pd.DataFrame(records)

            # TTP frequency table
            st.subheader("TTP Hit Frequency")
            df["ttp_id"] = df["mitre_enriched"].apply(lambda x: x.get("ttp_id", "Unknown"))
            df["ttp_name"] = df["mitre_enriched"].apply(lambda x: x.get("ttp_name", "Unknown"))
            ttp_counts = df["ttp_id"].value_counts().reset_index()
            ttp_counts.columns = ["TTP", "Count"]
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.dataframe(ttp_counts, use_container_width=True)
            with col2:
                fig = px.bar(ttp_counts, x="TTP", y="Count", template="plotly_dark",
                             color_discrete_sequence=["#ff4b4b"])
                fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)

            # Navigator layer download
            st.divider()
            st.subheader("MITRE Navigator Layer")
            layer = generate_navigator_layer(records)
            #st.write(layer)#debug
            layer_json = json.dumps(layer, indent=2)
            st.download_button(
                label="⬇️ Download Navigator Layer",
                data=layer_json,
                file_name="clinicalshield_navigator.json",
                mime="application/json"
            )
            
            st.caption("Import this file at https://mitre-attack.github.io/attack-navigator/")

    except FileNotFoundError:
        st.warning("No classifications found. Run a simulation first.")

elif page == "Generate Report":
    from report_generator import generate_pdf_report
    st.title("📄 Generate Threat Report")
    st.caption("A summary of all threats detected")

    try:
        records = []
        with open("results/classifications.jsonl", "r") as f:
            for line in f:
                records.append(json.loads(line))

        df = pd.DataFrame(records)
        df["is_attack"] = df["prediction"].apply(lambda x: x.get("is_attack", False))
        df["severity"] = df["prediction"].apply(lambda x: x.get("severity", ""))
        df["vector_type"] = df["prediction"].apply(lambda x: x.get("vector_type", ""))
        attacks = df[df["is_attack"] == True]

        st.subheader("Session Summary")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Records", len(df))
        col2.metric("Attacks Detected", len(attacks))
        col3.metric("Detection Rate", f"{round(len(attacks)/len(df)*100, 1)}%")
        col4.metric("Critical", len(attacks[attacks["severity"] == "critical"]))

        st.divider()
        st.subheader("Severity Breakdown")
        severity_counts = attacks["severity"].value_counts().reset_index()
        severity_counts.columns = ["Severity", "Count"]
        fig = px.bar(severity_counts, x="Severity", y="Count", 
            color="Severity",
            color_discrete_map={"critical": "#ff0000", "high": "#ff4b4b", "medium": "#ff8c00", "low": "#ffd700"},
            template="plotly_dark")
        fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Severity Distribution")
            fig_pie = px.pie(severity_counts, names="Severity", values="Count",
                             color="Severity",
                             color_discrete_map={"critical": "#ff0000", "high": "#ff4b4b", "medium": "#ff8c00", "low": "#ffd700"},
                             template="plotly_dark",
                             hole=0.4)
            fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_pie, use_container_width=True)
        with col2:
            st.subheader("Confidence Score Distribution")
            attacks["confidence"] = attacks["prediction"].apply(lambda x: x.get("confidence", 0))
            fig_conf = px.histogram(attacks, x="confidence", nbins=20,
                                    template="plotly_dark",
                                    color_discrete_sequence=["#ff4b4b"])
            fig_conf.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_conf, use_container_width=True)

        st.divider()
        st.subheader("Top Attack Vectors")
        vector_counts = attacks["vector_type"].value_counts().reset_index()
        vector_counts.columns = ["Vector", "Count"]
        st.dataframe(vector_counts, use_container_width=True)

        st.divider()
        report_json = attacks.to_json(orient="records", indent=2)
        st.download_button(
            label="⬇️ Download Report (JSON)",
            data=report_json,
            file_name="clinicalshield_report.json",
            mime="application/json"
        )

        st.divider()
        if st.button("📄 Generate PDF Report"):
            with st.spinner("Generating PDF..."):
                os.makedirs("outputs", exist_ok=True)
                pdf_path = generate_pdf_report(records)
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=f,
                        file_name="clinicalshield_report.pdf",
                        mime="application/pdf"
                    )

    except FileNotFoundError:
        st.warning("No classifications found. Run a simulation first.")


