from pathlib import Path
s=Path('dashboard/index.html').read_text()
for x in ['G3 bounded diagnostics','g3-controller.json','g3-execution.json','target mutation OFF']:
 assert x in s,x
print('4 Control Room G3 contract assertions passed')
