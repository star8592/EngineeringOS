import sys; sys.path.insert(0,'src/engineeringos')
from facts import Fact, contradictions

def f(value,scope='production'):
    return Fact('x','version',value,scope,'t','test','id','test')

def main():
    assert len(contradictions([f('1'),f('2')])) == 1
    assert contradictions([f('1','repository'),f('2','production')]) == []
    print('2 fact-registry invariants passed')
if __name__=='__main__': main()
