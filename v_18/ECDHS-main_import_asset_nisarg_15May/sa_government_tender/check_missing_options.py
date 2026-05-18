#!/usr/bin/env python3
"""
Script to check which many2one fields in XML files are missing the required options.
"""

import os
import re
from pathlib import Path

# First, collect all many2one field names from Python models
many2one_fields = set()

models_dir = Path('models')
if models_dir.exists():
    for py_file in models_dir.glob('*.py'):
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Find all Many2one field definitions
            matches = re.findall(r'(\w+)\s*=\s*fields\.Many2one', content)
            many2one_fields.update(matches)

print(f"Found {len(many2one_fields)} many2one field names from models")
print("Many2one fields:", sorted(many2one_fields))
print()

# Now check XML files for fields without options
missing_options = []
REQUIRED_OPTIONS = "{'no_create': True,'no_quick_create': True,'no_create_edit': True}"

for directory in ['views', 'wizard']:
    dir_path = Path(directory)
    if dir_path.exists():
        for xml_file in dir_path.glob('*.xml'):
            with open(xml_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    # Look for field tags
                    field_match = re.search(r'<field\s+name="(\w+)"', line)
                    if field_match:
                        field_name = field_match.group(1)
                        # Check if it's a many2one field (ends with _id or _ids)
                        if field_name in many2one_fields:
                            # Check if this line or nearby lines have options
                            # We need to check multiline field definitions
                            full_field = line
                            j = i
                            # If the field tag doesn't close on this line, read more lines
                            while '/>' not in full_field and '>' not in full_field.split('<field')[1].split('</field>')[0] if '</field>' in full_field else True:
                                if j < len(lines):
                                    full_field += lines[j]
                                    j += 1
                                else:
                                    break

                            # Check if options exist
                            if 'options=' not in full_field:
                                # Skip if it's an ir.ui.view field definition or other metadata
                                if 'model_id' not in field_name and 'view_id' not in field_name and 'action_id' not in field_name:
                                    if 'inherit_id' not in field_name and 'parent_id' not in field_name and 'binding_model_id' not in field_name:
                                        if 'groups_id' not in field_name and 'search_view_id' not in field_name:
                                            missing_options.append((str(xml_file), i, field_name, line.strip()))

print(f"Found {len(missing_options)} many2one field instances without options:\n")
for filepath, line_no, field_name, line in missing_options:
    print(f"{filepath}:{line_no}")
    print(f"  Field: {field_name}")
    print(f"  Line: {line[:120]}...")
    print()

if missing_options:
    print(f"\nTotal: {len(missing_options)} instances need options added")
else:
    print("\nAll many2one fields have the required options! ✓")
