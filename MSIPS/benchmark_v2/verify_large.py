"""Reconstruct every constraint independently and check saved candidate selections."""
import numpy as np,json,csv
from pathlib import Path
P=Path(__file__).resolve().parent
ins=json.load(open(P/'large_instances.json'));rows=list(csv.DictReader(open(P/'large_results.csv')))
for v in ins:
 n=v['n'];a=np.array(v['a']);dom=np.array(v['domains']);pr=np.array(v['privacy']);c=np.array(v['cost'])
 def check(indices):
  if indices is None:return
  s=set(indices);assert all(any(i%4==f for i in s) for f in range(4));assert sum(pr[i] for i in s)<=v['budget']+1e-7
  for t in range(3):
   assert 1-np.prod([1-a[t,i] for i in s])>=.99-1e-7
   for d in range(len(dom)):
    r=[i for i in s if not dom[d,i]];assert any(i%4==0 for i in r)
    assert 1-np.prod([1-a[t,i] for i in r])>=.95-1e-7
 check(v['selected_exact']);check(v['selected_forward'])
 rr=next(r for r in rows if r['instance']==v['id'] and r['algorithm']=='forward_local')
 if v['selected_forward'] is not None:assert abs(sum(c[i] for i in v['selected_forward'])-float(rr['heuristic_cost']))<1e-8
print('PASS: all saved exact and forward-local selections satisfy independently reconstructed constraints.')
