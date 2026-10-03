import sys; sys.path.insert(0,'src/engineeringos')
from policy import source_production_drift

def main():
 assert source_production_drift('1','1',True,True).state=='OK'
 assert source_production_drift('2','1',True,True).state=='ACCEPTABLE_DRIFT'
 assert source_production_drift('2','1',False,True).state=='REVIEW'
 assert source_production_drift('2','1',True,False).state=='BLOCK'
 print('4 policy invariants passed')
if __name__=='__main__': main()
