import re

with open('data/demo_data.xml', 'r') as f:
    content = f.read()

lines = content.split('\n')
cleaned_lines = []
in_record = False
skip_until_record = False

for i, line in enumerate(lines):
    if '<record' in line:
        in_record = True
        skip_until_record = False
        cleaned_lines.append(line)
    elif '</record>' in line:
        in_record = False
        cleaned_lines.append(line)
    elif '<field' in line and not in_record and not skip_until_record:
        print(f"Skipping orphaned field at line {i+1}: {line.strip()[:60]}")
        skip_until_record = True
        continue
    elif not skip_until_record:
        cleaned_lines.append(line)

with open('data/demo_data.xml', 'w') as f:
    f.write('\n'.join(cleaned_lines))

print("\nFixed XML - orphaned fields removed")
