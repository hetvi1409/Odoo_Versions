#!/usr/bin/env python3
"""
Script to add options="{'no_create': True,'no_quick_create': True,'no_create_edit': True}"
to all many2one fields in XML files.
"""

import os
import re
from pathlib import Path

# Read many2one field names
with open('/tmp/many2one_fields.txt', 'r') as f:
    many2one_fields = set(line.strip() for line in f if line.strip())

print(f"Found {len(many2one_fields)} many2one field names")

# Define the options string to add
OPTIONS_STRING = "options=\"{'no_create': True,'no_quick_create': True,'no_create_edit': True}\""

def process_xml_file(filepath):
    """Process a single XML file to add options to many2one fields."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    modifications = 0

    for field_name in many2one_fields:
        # Pattern to match field tags with this name (self-closing or not)
        # Match: <field name="field_name" ... /> or <field name="field_name" ... >
        pattern = rf'(<field\s+name="{re.escape(field_name)}"(?:\s+[^>]*?)?)(/?>)'

        def replace_field(match):
            nonlocal modifications
            field_opening = match.group(1)
            field_closing = match.group(2)

            # Check if options already exists with all required settings
            if 'options=' in field_opening:
                # Check if all three options are present
                if "'no_create': True" in field_opening and "'no_quick_create': True" in field_opening and "'no_create_edit': True" in field_opening:
                    # Already has all options, don't modify
                    return match.group(0)
                else:
                    # Has options but incomplete, remove old options and add new
                    field_opening = re.sub(r'\s*options="[^"]*"', '', field_opening)
                    field_opening = re.sub(r"\s*options='[^']*'", '', field_opening)

            # Add options before the closing
            modifications += 1
            return f"{field_opening} {OPTIONS_STRING}{field_closing}"

        content = re.sub(pattern, replace_field, content)

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return modifications
    return 0

# Process all XML files in views and wizard directories
total_modifications = 0
files_modified = 0

for directory in ['views', 'wizard']:
    if os.path.exists(directory):
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if filename.endswith('.xml'):
                    filepath = os.path.join(root, filename)
                    mods = process_xml_file(filepath)
                    if mods > 0:
                        files_modified += 1
                        total_modifications += mods
                        print(f"Modified {filepath}: {mods} fields updated")

print(f"\n=== Summary ===")
print(f"Files modified: {files_modified}")
print(f"Total field instances updated: {total_modifications}")
