import sys;sys.path.insert(0,'src/engineeringos')
from git_adapter import inventory
i=inventory('/mnt/disk1/Code/CycleAlpha','CycleAlpha')
assert i['project']=='CycleAlpha'; assert len(i['facts'])>=2; assert isinstance(i['dirty'],bool); assert 'DevControl' not in open('src/engineeringos/git_adapter.py').read()
print('4 generic-adapter invariants passed')
