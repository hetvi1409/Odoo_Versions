from odoo import models, fields, _
import base64
import csv
from io import StringIO
from odoo.exceptions import ValidationError
import logging
from datetime import datetime
_logger = logging.getLogger(__name__)

class ValuationRollImportWizard(models.TransientModel):
    _name = 'valuation.roll.import.wizard'
    _description = 'Valuation Roll Import Wizard'

    csv_file = fields.Binary(string="CSV File")
    filename = fields.Char(string="File Name")

    def action_import_csv(self):
        # Decode the uploaded file
        decoded_file = base64.b64decode(self.csv_file)
        io_string = StringIO(decoded_file.decode('UTF-8'))
        reader = csv.DictReader(io_string)

        # Define the mapping of CSV columns to model fields
        field_mapping = {
            'Region ID': 'region_id',
            'Property Area Sqmt': 'building_area',
            'Owner Name': 'partner_id',
            'Property Status Description': 'status',
            'Usage': 'usage',
            'Address': 'address',
            'Town Name Key': 'town_name_key',
            'Town Name Description':'town_name_description',
            'Ward ID':'ward',
            'SG ID':'sg_id',
            'Erf Number':'erf_number',
            'Portion Number': 'portion_number',
            'Property Remainder Indicator': 'property_remainder_indicator',
            'Unit Type': 'unit_type',
            'SP Scheme Key':'sp_scheme_key',
            'AT Scheme Key': 'at_scheme_key',
            'Scheme Year': 'scheme_year',
            'Scheme Name': 'scheme_name',
            'Reflect On At Scheme Property': 'reflect_on_scheme_property',
            'Unit Key': 'unit_key',
            'Unit Number': 'unit_number',
            'Premise ID': 'premise_id',
            'Unit Legal Are': 'unit_legal_area',
            'Participation Quota': 'participation_quota',
            'Lowest Stand SG ID': 'lowest_stand_sg_id',
            'Land Type Code': 'land_type_code',
            'Land Type Name': 'land_type_name',
            'Remainder Of Subdivision Indicator': 'remainder_of_subdivision',
            'Remainder Of Township Indicator': 'remainder_of_township',
            'TPS Code': 'tps_name',
            'Zoning Property Key': 'zoning_property_key',
            'Zone Code': 'zone_code',
            'Zone Description':'zoning_id',
            'Zoning Effective Date': 'zoning_effective_date',
            'Multiple Zoning Count': 'multiple_zoning_count',
            'Address Key': 'address_key',
            'Street Key': 'street_key',
            'Street Number': 'street_number',
            'Street Type': 'street_type',
            'Street Type Name': 'street_type_name',
            'Scheme - Primary Address SG ID': 'scheme_primary_address_sg_id',
            'Multiple Active Addresses Count': 'multiple_active_addresses_count',
            'Building Plan Date': 'building_plan_date',
            'Building Plan Ref': 'building_plan_ref',
            'Occupancy Cert Date': 'occupancy_cert_date',
            'Occupancy Cert ID': 'occupancy_cert_id',
            'Total Engineering Payable Amount': 'total_engineering_payable_amount',
            'Engineering Paid Indicator': 'engineering_paid_indicator',
            'Engineering Paid Amount': 'engineering_paid_amount',
            'Valuation Roll Key': 'valuation_roll_key',
            'Roll Type': 'roll_type',
            'Valuation Implementation Date': 'valuation_implementation_date',
            'Valuation Key': 'valuation_key',
            'Valuation Type': 'valuation_type',
            'Valuation Type Description': 'valuation_type_description',
            'Valuation Date (Captured Date)': 'valuation_date_captured',
            'Valuation Effective Date (Wef Date)': 'valuation_effective_date',
            'Valuation Status': 'valuation_status',
            'CAT Code': 'cat_code',
            'CAT Description': 'cat_description',
            'LIS Application Key': 'lis_application_key',
            'Voucher Key': 'voucher_key',
            'Va3 Key': 'va3_key',
            'LIS Task Key': 'lis_task_key',
            'Valuation Value Key': 'valuation_value_key',
            'Rateable Area': 'rateable_area',
            'Market Value': 'market_value',
            'Remarks List Key': 'remarks_list_key',
            'Remark Description': 'remark_description',
            'Additional Notes': 'note',
            'TD Main Key': 'td_main_key',
            'Owner ID': 'owner_id_number',
            'Title Deed Number': 'title_deed_number',
            'Purchased Date': 'purchase_date',
            'Purchased Price': 'purchased_price',
            'Unit Rights Key': 'unit_rights_key',
            'Right Description': 'right_description',
            'Valuation Split Number': 'valuation_split_number',
            'Valuation Split Indicator': 'valuation_split_indicator',
            'Reason': 'valuation_reason',

            # Add additional mappings here...
        }

        # Fetch existing buildings with their JMC ASSET NUMBERs
        existing_buildings = self.env['building'].search([])  # Get all buildings
        building_dict = {building.jmc_number: building for building in existing_buildings}

        for row in reader:
            vals = {}
            jmc_number = row.get('JMC ASSET NUMBER')

            if not jmc_number:
                continue  # Skip this row if JMC ASSET NUMBER is not present

            # Check if the building exists in the dictionary
            building_record = building_dict.get(jmc_number)

            for csv_field, model_field in field_mapping.items():
                if csv_field in row and row[csv_field]:  # Check if the CSV field is present and not empty
                    if model_field == 'region_id':
                        region_name = f"Region {row[csv_field]}"  # Adjust the region name format
                        region_record = self.env['regions'].search([('name', '=', region_name)], limit=1)

                        if region_record:
                            vals[model_field] = region_record.id  # If found, assign the existing region ID
                        else:
                            # If not found, create a new region with the adjusted name
                            new_region = self.env['regions'].create({'name': region_name})
                            vals[model_field] = new_region.id  # Assign the new region ID
                    elif model_field == 'partner_id':
                        vals[model_field] = self.env['res.partner'].search([('name', '=', row[csv_field])], limit=1).id
                    elif model_field == 'building_plan_date':
                        vals[model_field] = datetime.strptime(row[csv_field], '%d %m %Y').strftime('%Y-%m-%d')
                    elif model_field == 'zoning_effective_date':
                        date_str = row[csv_field]
                        if len(date_str) == 10:  # Checking for '01 01 1900' format
                            vals[model_field] = datetime.strptime(date_str, '%d %m %Y').strftime('%Y-%m-%d')
                        else:
                            vals[model_field] = datetime.strptime(date_str, '%d/%m/%Y %H:%M').strftime(
                                '%Y-%m-%d %H:%M:%S')
                    elif model_field in ['valuation_implementation_date', 'valuation_date_captured','valuation_effective_date','occupancy_cert_date','purchase_date']:
                        vals[model_field] = datetime.strptime(row[csv_field], '%d %m %Y').strftime('%Y-%m-%d')
                    elif model_field == 'status':
                        status_record = self.env['building.status'].search([('name', '=', row[csv_field])], limit=1)
                        if status_record:
                            vals[model_field] = status_record.id  # Use existing status ID
                        else:
                            # Create a new status record if it does not exist
                            new_status = self.env['building.status'].create({'name': row[csv_field]})
                            vals[model_field] = new_status.id  # Assign the new status ID
                    elif model_field == 'usage':
                        vals[model_field] = row[csv_field]  # Assuming the value matches the selection in usage
                    elif model_field == 'zoning_id':
                        zoning_record = self.env['property.zoning'].search([('name', '=', row[csv_field])], limit=1)
                        if zoning_record:
                            vals[model_field] = zoning_record.id  # Use existing status ID
                        else:
                            # Create a new status record if it does not exist
                            zoning_record = self.env['property.zoning'].create({'name': row[csv_field]})
                    else:
                        vals[model_field] = row[csv_field]  # Direct mapping for other fields

            if building_record:
                # Update existing record
                building_record.write(vals)
            else:
                # Create a new building record
                _logger.info('sdadsdda')
                pass

