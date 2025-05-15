import streamlit as st
import os
from tempfile import NamedTemporaryFile
from extractor_core import (
    extract_text_from_pdf,
    chunk_text,
    extract_clinical_info,
    generate_xml
)

st.set_page_config(page_title="Clinical Trial Protocol Extractor", layout="wide")
st.title("Clinical Trial Protocol Extractor")

uploaded_file = st.file_uploader("Upload a clinical trial PDF", type=["pdf"])

if uploaded_file:
    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        pdf_path = tmp_file.name

    st.success(f"Uploaded: {uploaded_file.name}")

    with st.spinner("Extracting clinical trial info..."):
        try:
            pdf_text = extract_text_from_pdf(pdf_path)
            chunks = chunk_text(pdf_text)
            clinical_info = extract_clinical_info(chunks)
        except Exception as e:
            st.error(f"Error extracting info: {e}")
            st.stop()

    # Make editable fields grouped in expanders
    with st.expander("📄 Titles"):
        clinical_info["brief_title"] = st.text_input("Brief Title", clinical_info.get("brief_title", ""))
        clinical_info["official_title"] = st.text_area("Official Title", clinical_info.get("official_title", ""))
        clinical_info["acronym"] = st.text_input("Acronym", clinical_info.get("acronym", ""))

    with st.expander("📐 Study Design"):
        study_type = clinical_info.get("study_design", {}).get("study_type", "")
        st.text(f"Study Type: {study_type}")
        if study_type == "Interventional":
            design = clinical_info["study_design"].get("interventional_design", {})
            design["interventional_subtype"] = st.text_input("Subtype", design.get("interventional_subtype", ""))
            design["phase"] = st.text_input("Phase", design.get("phase", ""))
            design["assignment"] = st.text_input("Assignment", design.get("assignment", ""))
            design["allocation"] = st.text_input("Allocation", design.get("allocation", ""))
            clinical_info["study_design"]["interventional_design"] = design
        elif study_type == "Observational":
            design = clinical_info["study_design"].get("observational_design", {})
            design["observational_study_design"] = st.text_input("Study Design", design.get("observational_study_design", ""))
            design["timing"] = st.text_input("Timing", design.get("timing", ""))
            design["biospecimen_retention"] = st.text_input("Biospecimen Retention", design.get("biospecimen_retention", ""))
            design["number_of_groups"] = st.text_input("# Groups", design.get("number_of_groups", ""))
            clinical_info["study_design"]["observational_design"] = design

    with st.expander("🧬 Eligibility"):
        elig = clinical_info.get("eligibility", {})
        elig["criteria"] = st.text_area("Eligibility Criteria", elig.get("criteria", ""))
        elig["gender"] = st.text_input("Gender", elig.get("gender", ""))
        elig["minimum_age"] = st.text_input("Min Age", elig.get("minimum_age", ""))
        elig["maximum_age"] = st.text_input("Max Age", elig.get("maximum_age", ""))
        elig["healthy_volunteers"] = st.text_input("Healthy Volunteers", elig.get("healthy_volunteers", ""))
        clinical_info["eligibility"] = elig

    with st.expander("🎯 Outcomes"):
        st.markdown("**Primary Outcomes**")
        for i, outcome in enumerate(clinical_info.get("primary_outcomes", [])):
            outcome["outcome_measure"] = st.text_input(f"Primary Measure {i+1}", outcome.get("outcome_measure", ""))
            outcome["outcome_time_frame"] = st.text_input(f"Time Frame {i+1}", outcome.get("outcome_time_frame", ""))
            outcome["outcome_description"] = st.text_area(f"Description {i+1}", outcome.get("outcome_description", ""))
        st.markdown("**Secondary Outcomes**")
        for i, outcome in enumerate(clinical_info.get("secondary_outcomes", [])):
            outcome["outcome_measure"] = st.text_input(f"Secondary Measure {i+1}", outcome.get("outcome_measure", ""))
            outcome["outcome_time_frame"] = st.text_input(f"Time Frame {i+1}", outcome.get("outcome_time_frame", ""))
            outcome["outcome_description"] = st.text_area(f"Description {i+1}", outcome.get("outcome_description", ""))

    with st.expander("💊 Interventions & Arms"):
        for i, arm in enumerate(clinical_info.get("arm_groups", [])):
            st.text_input(f"Arm Group Label {i+1}", arm.get("arm_group_label", ""))
            st.text_input(f"Arm Type {i+1}", arm.get("arm_type", ""))
            st.text_area(f"Arm Description {i+1}", arm.get("arm_group_description", ""))
        for i, intv in enumerate(clinical_info.get("interventions", [])):
            st.text_input(f"Intervention Name {i+1}", intv.get("intervention_name", ""))
            st.text_input(f"Intervention Type {i+1}", intv.get("intervention_type", ""))
            st.text_area(f"Intervention Description {i+1}", intv.get("intervention_description", ""))

    with st.expander("🏢 Sponsor Info"):
        sponsor = clinical_info.get("sponsors", {})
        st.text_input("Lead Sponsor", sponsor.get("lead_sponsor", ""))
        st.text_area("Collaborators", ", ".join(sponsor.get("collaborators", [])))

    with st.expander("📆 Study Metadata"):
        st.text_input("Org Study ID", clinical_info.get("org_study_id", ""))
        st.text_input("Enrollment", clinical_info.get("enrollment", ""))
        st.text_input("Enrollment Type", clinical_info.get("enrollment_type", ""))
        st.text_input("Overall Status", clinical_info.get("overall_status", ""))
        st.text_input("Start Date", clinical_info.get("start_date", ""))
        st.text_input("Primary Completion Date", clinical_info.get("primary_compl_date", ""))
        st.text_area("Conditions", ", ".join(clinical_info.get("conditions", [])))
        st.text_area("Keywords", ", ".join(clinical_info.get("keywords", [])))

    with st.expander("📝 Study Summary"):
        st.text_area("Brief Summary", clinical_info.get("brief_summary", ""))
        st.text_area("Detailed Description", clinical_info.get("detailed_description", ""))

    # Final button to generate XML
    if st.button("Generate XML and Download"):
        with st.spinner("Generating XML..."):
            xml_string = generate_xml(clinical_info)
            st.download_button("📥 Download XML", data=xml_string, file_name="clinical_trial.xml", mime="text/xml")
            st.text_area("Preview XML", xml_string, height=300)
