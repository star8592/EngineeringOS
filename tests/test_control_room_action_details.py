from pathlib import Path
s=Path('dashboard/index.html').read_text()
for required in ['Evidence drill-down','runtime/action-details.json','suggested_resolution','evidence_count']:
    assert required in s, required
assert 'target_mutation_authorized' not in s or 'Target mutation' in s
print('4 Control Room action-detail contract assertions passed')
