from odoo import models, fields, _
import base64
from openpyxl import load_workbook
from odoo.exceptions import UserError
import io
from datetime import date


class AssetImportWizard(models.TransientModel):
    _name = 'asset.import.wizard'
    _description = 'Import Asset'

    file = fields.Binary("Excel File", required=True)
    filename = fields.Char('File Name')


    def action_import(self):
        if not self.file:
            raise UserError(_("Please upload an Excel file."))

        data = base64.b64decode(self.file)

        # LOAD WORKBOOK
        try:
            wb = load_workbook(filename=io.BytesIO(data), data_only=True)
        except Exception as e:
            raise UserError(_("Invalid Excel file: %s") % str(e))

        # sheet_name = "Computer Equipment - Adj"
        # if sheet_name not in wb.sheetnames:
        #     raise UserError(_(f"Sheet '{sheet_name}' does not exist in the file."))

        # sheet = wb[sheet_name]

        sheet = wb.active

        # HEADER ROW
        header_row = next(sheet.iter_rows(min_row=7, max_row=7, values_only=True))
        print("header_row----->",header_row)

        # HELPER FUNCTION
        def clean_condition(value):
            """ N/A , Not found and None return empty string """
            if not value:
                return ""
            value = str(value).strip()
            if value.lower() in ["n/a", "not found", "na","none"]:
                return " "
            return value

        # FIND COLUMN INDEXES
        col_index = {
            "location": None,
            "building": None,
            "barcode": None,
            "description": None,
            "serial": None,
            "category": None,
            "notes": None,
            "cost_price": None,
            "employee": None,
            "invpoice_number": None,
            "supplier": None,
            "date_of_purchase": None,
            "condition_2020": None,
            "condition_2021": None,
            "condition_2022": None,
            "condition_2023": None,
            "condition_2024": None,
        }

        for idx, col_name in enumerate(header_row):
            if col_name == "Location":
                col_index["location"] = idx
            elif col_name == "Building":
                col_index["building"] = idx
            elif col_name == "Barcode":
                col_index["barcode"] = idx
            elif col_name == "Description":
                col_index["description"] = idx
            elif col_name == "SerialNo":
                col_index["serial"] = idx
            elif col_name == " 2020/21 Condition":
                col_index["condition_2020"] = idx
            elif col_name == "2021/2022 Condition":
                col_index["condition_2021"] = idx
            elif col_name == "2022/2023 Condition":
                col_index["condition_2022"] = idx
            elif col_name == "2023/2024 Condition":
                col_index["condition_2023"] = idx
            elif col_name == "2024/2025 Condition":
                col_index["condition_2024"] = idx

            elif col_name == "Category":
                col_index["category"] = idx
            elif col_name == "Notes/comment":
                col_index["notes"] = idx
            elif col_name == "Cost Price":
                col_index["cost_price"] = idx
            elif col_name == "Date of purchase":
                col_index["date_of_purchase"] = idx
            elif col_name == "Responsible Official":
                col_index["employee"] = idx
            elif col_name == "Invoice number":
                col_index["invoice_number"] = idx
            elif col_name == "Supplier":
                col_index["supplier"] = idx
            elif col_name == "Additional Description":
                col_index["detailed_description"] = idx



        missing_columns = [key for key, value in col_index.items() if value is None]
        if missing_columns:
            print("missing_columns----->",missing_columns)
            # raise UserError(_(f"Required columns not found: {', '.join(missing_columns)}"))

            has_barcode_column = col_index.get("barcode") is not None
            print("has_barcode_column----->",has_barcode_column)

        AssetLocation = self.env["asset.verification.job.location"]
        AssetBuilding = self.env["asset.verification.job.building"]
        AccountAsset = self.env["account.asset"]
        AssetHistory = self.env["asset.verification.history"]

        created_locations = created_buildings = created_assets = created_category = created_employee = 0

        # PROCESS ROWS
        for row in sheet.iter_rows(min_row=8, values_only=True):

            description = row[col_index["description"]]
            if not has_barcode_column:
                detailed_description = row[col_index["detailed_description"]]
                print("NOT BARCODE---",row)
                AccountAsset.create({
                    "name": str(description).strip(),
                    "description": detailed_description,
                    "account_depreciation_expense_id": self.env.ref('asset_import.exp_account').id,
                    "account_depreciation_id": self.env.ref('asset_import.dep_account').id,
                })
                created_assets += 1

            # IMPORT EMPLOYEE
            if col_index["employee"] is None:
                continue
            employee_value = row[col_index["employee"]]
            employee_rec = False
            if employee_value:
                employee_name = str(employee_value).strip()
                employee_rec = self.env['hr.employee'].search([
                    ("name", "=", employee_name)
                ], limit=1)
                if not employee_rec:
                    employee_rec = self.env['hr.employee'].create({"name": employee_name})
                    created_employee += 1


            # IMPORT BUILDING
            if col_index["building"] is None:
                continue
            building_value = row[col_index["building"]]
            building_rec = False

            if building_value:
                building_name = str(building_value).strip()
                building_rec = AssetBuilding.search(
                    [("name", "=", building_name)],
                    limit=1
                )
                if not building_rec:
                    building_rec = AssetBuilding.create({
                        "name": building_name
                    })
                    created_buildings += 1

            # IMPORT LOCATION
            if col_index["location"] is None:
                continue
            location_value = row[col_index["location"]]
            location_rec = False
            if location_value:
                location_name = str(location_value).strip()

                location_rec = AssetLocation.search([
                    ("name", "=", location_name),
                ], limit=1)

                if not location_rec:
                    location_rec = AssetLocation.create({
                        "name": location_name,
                        "building_id": building_rec.id if building_rec else False,
                    })
                    created_locations += 1
                else:
                    if building_rec and location_rec.building_id != building_rec:
                        location_rec.write({
                            "building_id": building_rec.id
                        })

            # IMPORT CATEGORY
            if col_index["category"] is None:
                continue
            category_value = clean_condition(row[col_index["category"]])
            category_rec = False
            if category_value:
                category_name = str(category_value).strip()
                category_rec = self.env['asset.category'].search([
                    ("name", "ilike", category_name)
                ], limit=1)

                if not category_rec:
                    category_rec = self.env['asset.category'].create({
                        "name": category_name,
                        "is_movable": True,  # Default to movable, adjust as needed
                    })
                    created_category += 1

            # IMPORT SUPPLIER
            if col_index["supplier"] is None:
                continue
            supplier_value = clean_condition(row[col_index["supplier"]])
            supplier_rec = False
            # here we check if supplier_value is not empty or just whitespace
            if supplier_value and not supplier_value.isspace():
                supplier_rec = self.env['res.partner'].search([
                    ("name", "=", supplier_value)
                ], limit=1)

                if not supplier_rec:
                    supplier_rec = self.env['res.partner'].create({
                        "name": supplier_value,
                    })


            # IMPORT ASSETS
            barcode = row[col_index["barcode"]]
            description = row[col_index["description"]]
            serial = clean_condition(row[col_index["serial"]])
            category = row[col_index["category"]]
            notes = row[col_index["notes"]]
            cost_price = row[col_index["cost_price"]]
            date_of_purchase = row[col_index["date_of_purchase"]]
            invoice_number = clean_condition(row[col_index["invoice_number"]])

            if not (barcode or description or serial):
                continue


            # location
            location_id = False
            if location_value:
                location_rec = AssetLocation.search([("name", "=", location_name)], limit=1)
                location_id = location_rec.id if location_rec else False

            #category
            category = False
            if category_value:
                category_name = str(category_value).strip()
                category = self.env['asset.category'].search([
                    ("name", "ilike", category_name)
                ], limit=1).id

            # employee
            custodian_id = False
            if employee_rec:
                custodian_id = employee_rec.id

            vals = {
                "alternative_ref": barcode and str(barcode).strip(),
                "name": description and str(description).strip() or "No Description",
                "serial_number": serial and str(serial).strip(),
                "job_location_id": location_id,
                "afs_classification": category,
                "classification_type": False,  # Will be set in create method
                "notes": notes and str(notes).strip(),
                "original_value": cost_price if isinstance(cost_price, (int, float)) else 0.0,
                "acquisition_date": date_of_purchase,
                "prorata_date" : date.today(),
                "custodian_id": custodian_id,
                "invoice_number": invoice_number,
                "supplier_id": supplier_rec.id if supplier_rec else False,
                "account_depreciation_expense_id": self.env.ref('asset_import.exp_account').id,
                "account_depreciation_id": self.env.ref('asset_import.dep_account').id,
            }

            # Check duplicate assets
            domain = []
            if vals["alternative_ref"]:
                domain.append(("alternative_ref", "=", vals["alternative_ref"]))
            # if vals["serial_number"]:
            #     domain.append(("serial_number", "=", vals["serial_number"]))

            exists_asset = AccountAsset.search(domain, limit=1) if domain else False

            if not exists_asset:
                asset = AccountAsset.create(vals)
                created_assets += 1
            else:
                asset = exists_asset
                asset.write({"job_location_id": location_id,
                             "prorata_date" : date.today(),
                             "acquisition_date": date_of_purchase,
                             "afs_classification": category,
                             "account_depreciation_expense_id": self.env.ref('asset_import.exp_account').id,
                             "account_depreciation_id": self.env.ref('asset_import.dep_account').id,})

            # Check if all condition columns exist and all values are None/empty
            all_conditions_empty = True
            if (col_index["condition_2020"] is not None and
                col_index["condition_2021"] is not None and
                col_index["condition_2022"] is not None and
                col_index["condition_2023"] is not None and
                col_index["condition_2024"] is not None):

                if (row[col_index["condition_2020"]] or
                    row[col_index["condition_2021"]] or
                    row[col_index["condition_2022"]] or
                    row[col_index["condition_2023"]] or
                    row[col_index["condition_2024"]]):
                    all_conditions_empty = False

            if all_conditions_empty and all(col_index[f"condition_{year}"] is None for year in ["2020", "2021", "2022", "2023", "2024"]):
                continue

            # IMPORT HISTORY
            cond_2020 = clean_condition(row[col_index["condition_2020"]])
            cond_2021 = clean_condition(row[col_index["condition_2021"]])
            cond_2022 = clean_condition(row[col_index["condition_2022"]])
            cond_2023 = clean_condition(row[col_index["condition_2023"]])
            cond_2024 = clean_condition(row[col_index["condition_2024"]])

            # Year-label mapping (Past Year, This Year)
            year_data = [
                ("2020", "2021", cond_2020, cond_2021),
                ("2021", "2022", cond_2021, cond_2022),
                ("2022", "2023", cond_2022, cond_2023),
                ("2023", "2024", cond_2023, cond_2024),
                ("2024", "2025", cond_2024, ""),  # last year has no next condition
            ]

            barcode_str = barcode and str(barcode).strip() or ""

            for past_year, this_year, past_cond, current_cond in year_data:

                # Skip empty condition rows completely (optional but recommended)
                if not past_cond and not current_cond:
                    continue

                # CHECK IF HISTORY ALREADY EXISTS
                existing_history = AssetHistory.search([
                    ("history_id", "=", asset.id),
                    ("parent_barcode", "=", barcode_str),
                    ("past_year", "=", past_year),
                    ("this_year", "=", this_year),
                ], limit=1)

                if existing_history:
                    print("existing----->",existing_history)
                    # Do NOT duplicate
                    continue

                AssetHistory.create({
                    "history_id": asset.id,
                    # "current_condition_past_year": past_cond,
                    # "current_condition_this_year": current_cond,
                    "comments": past_cond,
                    "is_verified": True,
                    "parent_barcode": barcode_str,
                    "past_year": past_year,
                    "this_year": this_year,
                })

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Import Completed",
                "message": (
                    f"{created_locations} Locations imported, "
                    f"{created_buildings} Buildings imported, "
                    f"{created_assets} Assets created successfully."
                    f"{created_category} Categories created successfully."
                    f"{created_employee} Employees created successfully."
                ),
                "type": "success",
            },
        }