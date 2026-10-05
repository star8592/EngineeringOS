from pathlib import Path
s=Path('dashboard/index.html').read_text()
for required in ['AI开发经理','产品工作台','你的产品','data-view="products"','data-view="chat"','data-view="progress"','data-view="decisions"','data-view="settings"','./runtime/commercial.json','接入现有产品','当前商业壳层为只读验收版']:
 assert required in s,required
primary=s[:s.index('<section class="view" id="view-settings">')]
for hidden in ('source_sha','source_head','Command receipts & outcome evidence','System-One · open shadow routing','G3 bounded diagnostics'):
 assert hidden not in primary,hidden
assert '<details class="engineering-shell"><summary>工程详情</summary>' in s
print('15 commercial-shell invariants passed')
