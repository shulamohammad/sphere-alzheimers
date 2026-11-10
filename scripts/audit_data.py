"""Audit the initial two SPHERE tables without exposing individual records."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def audit():
    tables, manifest = {}, {}
    for name in ('demographics_diagnosis.csv', 'biomarkers.csv'):
        path = ROOT / 'data' / 'raw' / name
        with path.open(newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            columns = reader.fieldnames
            if not columns or len(columns) != len(set(columns)):
                raise ValueError(f'Invalid or duplicate headers: {name}')
            rows = list(reader)
        if any(None in row or None in row.values() for row in rows):
            raise ValueError(f'Ragged rows in {name}')
        ids = [r['adrc_id'] for r in rows]
        if any(not i.strip() for i in ids) or len(ids) != len(set(ids)):
            raise ValueError(f'Missing/duplicate participant IDs: {name}')
        tables[name] = rows
        manifest[name] = {
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'rows': len(rows), 'columns': columns,
            'unique_ids': len(set(ids)),
            'blank_or_text_missing_counts': {
                c: sum(r[c].strip().lower() in ('', 'na', 'nan', 'null', 'n/a') for r in rows)
                for c in columns},
        }
    demo, bio = tables.values()
    demo_ids = {r['adrc_id'] for r in demo}
    bio_ids = {r['adrc_id'] for r in bio}
    result = {
        'source': 'https://adrc-sphere.stanford.edu/',
        'audit_date': '2026-11-08',
        'files': manifest,
        'diagnosis_counts': dict(Counter(r['diagnosis_consensus'] for r in demo)),
        'matched_diagnosis_counts': dict(Counter(r['diagnosis_consensus'] for r in demo if r['adrc_id'] in bio_ids)),
        'matched_participants': len(demo_ids & bio_ids),
        'demographics_without_biomarkers': len(demo_ids - bio_ids),
        'biomarkers_without_demographics': len(bio_ids - demo_ids),
        'excluded_diagnosis_predictors': [c for c in manifest['demographics_diagnosis.csv']['columns'] if c.startswith('diagnosis_consensus')],
        'limitations': ['Numeric missing-value codes and units are not yet verified against dictionary.', 'Synthetic-data dependence and label semantics require review before modeling.'],
    }
    out = ROOT / 'outputs' / 'initial_audit.json'
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('files','excluded_diagnosis_predictors')}, indent=2))

if __name__ == '__main__':
    audit()
