import PyPDF2
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

for pdf_file in pdf_files:
    if os.path.exists(pdf_file):
        print(f"\n{'='*80}")
        print(f"FILE: {pdf_file}")
        print('='*80)
        try:
            with open(pdf_file, 'rb') as file:
                pdf_reader = PyPDF2.PdfFileReader(file)
                print(f"Pages: {pdf_reader.numPages}\n")
                for i in range(pdf_reader.numPages):
                    page = pdf_reader.getPage(i)
                    text = page.extractText()
                    if text.strip():
                        print(f"--- Page {i+1} ---")
                        print(text)
                        print()
        except Exception as e:
            print(f"Error reading {pdf_file}: {e}")
    else:
        print(f"\nWARNING: {pdf_file} not found")