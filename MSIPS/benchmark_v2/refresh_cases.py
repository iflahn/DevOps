import json,copy,itertools
from pathlib import Path
P=Path(__file__).resolve().parent
c=json.load(open(P/'scenario_results.json'))['technician']['inputs']
def opt(td,c):
 good=[]
 for bits in itertools.product([0,1],repeat=len(c['items'])):
  s=[i for i,v in enumerate(bits) if v]
  if 0 not in s:continue
  def A(s,t):
   z=1
   for i in s:z*=1-c['a'][t][i]
   return 1-z
  nom=min(A(s,t) for t in range(2));r=min(A([i for i in s if d not in c['domains'][i]],t) for t in range(2) for d in {d for v in c['domains'] for d in v})
  if nom>=.95-1e-9 and r>=td-1e-9:good.append((sum(c['burden'][i] for i in s),s,nom,r))
 if not good:return ['infeasible','—','—','—']
 b,s,nom,r=min(good);return [','.join('p'+str(i+1) for i in s),b,round(nom,6),round(r,6)]
out={'threshold':[[t,*opt(t,c)] for t in [0,.2,.8,.9,.92,.93,.95]],'approval':[]}
for a in [.7,.75,.8,.9,.95]:
 cc=copy.deepcopy(c);cc['a'][1][2]=a;out['approval'].append([a,*opt(.8,cc)])
json.dump(out,open(P/'case_sensitivity.json','w'),indent=2);print(json.dumps(out))
