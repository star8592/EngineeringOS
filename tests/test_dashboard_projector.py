import sys,tempfile,pathlib,json,os
sys.path.insert(0,'src/engineeringos')
from dashboard_projector import atomic_copy_json,optional_copy_json
with tempfile.TemporaryDirectory() as d:
 d=pathlib.Path(d);a=d/'a.json';b=d/'nested'/'b.json';a.write_text(json.dumps({'x':1}))
 x=atomic_copy_json(a,b);assert x=={'x':1} and json.load(open(b))=={'x':1}
 assert not list(b.parent.glob('*.tmp'))
 assert optional_copy_json(d/'missing.json',d/'missing-out.json') is None
 assert not (d/'missing-out.json').exists()
html=pathlib.Path('dashboard/index.html').read_text()
assert '<strong>最近完成</strong>' in html
assert 'id="recentCompletionText"' in html
assert 'completed_work_items' in html and 'recently_completed' in html
assert "verifiedStates.has" in html
assert '还没有已验证完成的工作，完成后会显示在这里。' in html
user_home=html[html.index('<section class="user-home">'):html.index('</section>')]
for engineering_term in ('Git','commit','SHA','source_head','source_sha'):
 assert engineering_term not in user_home
print('10 dashboard-projector invariants passed')
