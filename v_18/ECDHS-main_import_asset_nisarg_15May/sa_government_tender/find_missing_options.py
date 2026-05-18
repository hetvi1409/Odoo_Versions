#!/usr/bin/env python3
"""
Script to find which fields in XML are many2one but missing options
"""

import os
import re

# Read many2one field names from Python files
with open('/tmp/many2one_fields.txt', 'r') as f:
    many2one_fields = set(line.strip() for line in f if line.strip())

print(f"Checking {len(many2one_fields)} many2one fields")

fields_without_options = []

for directory in ['views', 'wizard']:
    if os.path.exists(directory):
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if filename.endswith('.xml'):
                    filepath = os.path.join(root, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line_no, line in enumerate(f, 1):
                            for field_name in many2one_fields:
                                # Match field with this name but without options
                                if f'name="{field_name}"' in line and 'options=' not in line:
                                    fields_without_options.append((filepath, line_no, field_name, line.strip()))

print(f"\nFound {len(fields_without_options)} many2one field instances without options:\n")
for filepath, line_no, field_name, line in fields_without_options[:20]:
    print(f"{filepath}:{line_no}: {field_name}")
    print(f"  {line[:100]}...")
    print()

print(f"\nTotal: {len(fields_without_options)} instances need options added")
