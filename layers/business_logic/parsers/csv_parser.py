import csv

def read_csv_smart_encoding(file_path):
    encodings = ['utf-8-sig', 'utf-8', 'cp1252', 'latin1', 'iso-8859-1']
    delimiters = [';', ',']

    for enc in encodings:
        for delim in delimiters:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    reader = csv.reader(f, delimiter=delim)
                    rows = [[cell.strip() for cell in r] for r in reader if any(cell.strip() for cell in r)]
                    if len(rows) > 0 and len(rows[0]) >= 1:
                        return rows
            except (UnicodeDecodeError, Exception):
                continue
    return []

class CSVParser:
    def parse(self, file_path):
        raw_fields = []
        rows = read_csv_smart_encoding(file_path)

        if not rows:
            return raw_fields

        first_row = rows[0]
        # Si es un CSV estilo lista de países/opciones o campos
        if len(first_row) >= 1:
            for idx, r in enumerate(rows):
                if not any(r):
                    continue
                label = r[0] if len(r) > 0 else f"Campo {idx+1}"
                raw_fields.append({
                    "id": f"field_csv_{idx+1}",
                    "label": label,
                    "type": "input",
                    "placeholder": "XXXX"
                })

        return raw_fields
