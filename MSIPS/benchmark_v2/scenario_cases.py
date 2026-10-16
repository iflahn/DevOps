"""Exact small scenario cases. Contributions and burdens are hypothetical.
These results concern residual scores, not continued authorization security.
"""
import itertools,json
from pathlib import Path
P=Path(__file__).resolve().parent
T=['remote_impersonator','stolen_phone']
cases={
 'technician':dict(items=['p1 credential','p2 phone OTP','p3 owner approval','p4 proximity','p5 independent registered key'],a=[[.9,.8,.85,.7,.9],[.2,0,.95,0,.9]],domains=[['phone','issuer'],['phone'],['owner'],['gateway'],['key']],burden=[3,2,3,5,4],required=[0]),
 'camera':dict(items=['c1 credential','c2 posture','c3 owner approval','c4 independent registered key'],a=[[.9,.8,.85,.9],[.15,0,.95,.9]],domains=[['device','issuer'],['device','attester'],['owner'],['key']],burden=[3,2,3,4],required=[0,1]),
 'door':dict(items=['d1 credential','d2 proximity','d3 owner approval','d4 second device'],a=[[.9,.7,.85,.9],[0,0,.95,.9]],domains=[['phone'],['gateway'],['owner'],['second']],burden=[3,2,3,4],required=[0,1])}
def scores(s,c):
 nom=[];res=[]
 for at in c['a']:
  def A(ids):
   p=1
   for i in ids:p*=1-at[i]
   return 1-p
  nom.append(A(s));res.append(min(A([i for i in s if d not in c['domains'][i]]) for d in sorted({d for v in c['domains'] for d in v})))
 return [round(v,8) for v in nom],[round(v,8) for v in res]
out={}
for name,c in cases.items():
 rows=[]
 for bits in itertools.product([0,1],repeat=len(c['items'])):
  s=[i for i,v in enumerate(bits) if v]
  if not set(c['required']).issubset(s):continue
  nom,res=scores(s,c);rows.append(dict(selected=[i+1 for i in s],burden=sum(c['burden'][i] for i in s),nominal=nom,residual=res,feasible=min(nom)>=.95-1e-9 and min(res)>=.8-1e-9))
 feasible=[r for r in rows if r['feasible']];best=min(feasible,key=lambda r:(r['burden'],len(r['selected']),r['selected'])) if feasible else None
 out[name]=dict(inputs=c,scenarios=T,theta=.95,theta_residual=.8,rows=rows,best=best)
print(json.dumps({k:v['best'] for k,v in out.items()},indent=2))
json.dump(out,open(P/'scenario_results.json','w'),indent=2)
