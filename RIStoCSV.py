import csv

def parse_ris_to_csv(ris_file_path, csv_file_path):
    records = []
    current_record = {}

    with open(ris_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            if line.startswith('TY  -'):
                if current_record:
                    records.append(current_record)
                current_record = {'TY': line[6:].strip()}
            elif line.startswith('ER  -'):
                if current_record:
                    records.append(current_record)
                current_record = {}
            else:
                if len(line) > 6 and '  - ' in line:
                    tag, value = line[:2].strip(), line[6:].strip()
                    if tag in current_record:
                        current_record[tag] += f"; {value}"
                    else:
                        current_record[tag] = value

    if records:
        fieldnames = sorted({key for record in records for key in record.keys()})
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)

csv_output_path = 'AllCadimaResearchPapersCSV-V2.csv'
ris_file_path = 'AllCadimaResearchPapersRIS.ris'
parse_ris_to_csv(ris_file_path, csv_output_path)


