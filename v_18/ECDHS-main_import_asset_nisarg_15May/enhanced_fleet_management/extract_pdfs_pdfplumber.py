import pdfplumber
import os

pdf_files = [
    "Checklist_for_accidents.pdf",
    "Checklist_for_lost_and_theft_Form.pdf",
    "FLEET_REGISTER_HUMAN_SETTLEMENTS.pdf",
    "GFMS_Vehicle_relief_form.pdf",
    "Human_Settlements_Odo_metres.pdf",
    "MANUAL_TRIP_AUTHORISATION_2018.pdf",
    "RT46_accident _form.pdf",
    "TRANSIT_SOLUTION_SERVICE_AND_MAINTANANCE.pdf",
    "Transport_request_form.pdf",
    "Trip_authority_Form.pdf",
    "Vehicle_checklist_form.pdf"
]

output_file = "pdf_detailed_content.txt"
with open(output_file, 'w', encoding='utf-8') as out:
    for pdf_file in pdf_files:
        if os.path.exists(pdf_file):
            out.write(f"\n{'='*80}\n")
            out.write(f"FILE: {pdf_file}\n")
            out.write('='*80 + '\n')
            try:
                with pdfplumber.open(pdf_file) as pdf:
                    out.write(f"Pages: {len(pdf.pages)}\n\n")
                    for i, page in enumerate(pdf.pages):
                        text = page.extract_text()
                        if text and text.strip():
                            out.write(f"--- Page {i+1} ---\n")
                            out.write(text + '\n\n')
            except Exception as e:
                out.write(f"Error reading {pdf_file}: {e}\n")
        else:
            out.write(f"\nWARNING: {pdf_file} not found\n")

print(f"Extraction complete. Output saved to {output_file}")
