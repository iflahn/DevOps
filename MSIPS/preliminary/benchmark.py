"""Reproduce MSIPS synthetic selection benchmark. Python 3; NumPy and SciPy required.
Run from this directory: python benchmark.py. All generated data are synthetic.
"""
import os
os.environ.setdefault('OMP_NUM_THREADS','1')
import numpy as np, scipy, time, json, csv, platform
from scipy.optimize import milp,Bounds,LinearConstraint
from pathlib import Path
OUT=Path(__file__).resolve().parent
SEED=20261016; REPS=20
rng=np.random.default_rng(SEED)
records=[]; instances=[]
def solve(b,M,lb,ub,objective=True):
 t=time.perf_counter();r=milp(c=b if objective else np.zeros(len(b)),integrality=np.ones(len(b)),bounds=Bounds(0,1),constraints=LinearConstraint(M,lb,ub),options={'time_limit':2.0,'mip_rel_gap':0.0,'presolve':True});dt=time.perf_counter()-t
 x=None if r.x is None else (r.x>.5).astype(float)
 return r,x,dt
for n in [10,20,30]:
 for shape in ['separate','clustered','overlap']:
  for rep in range(REPS):
   d=max(3,n//5);dom=np.zeros((d,n))
   if shape=='separate':
    d=n;dom=np.eye(n)
   elif shape=='clustered':
    for i in range(n):dom[i%d,i]=1
   else:
    for i in range(n):dom[rng.choice(d,size=2,replace=False),i]=1
   a=rng.uniform(.35,.9,(3,n));w=-np.log1p(-a)
   b=rng.integers(1,11,n).astype(float);privacy=rng.integers(1,6,n).astype(float)
   F=np.zeros((2,n));F[0,:n//2]=1;F[1,n//2:]=1
   # nominal score >=.95 under each of three synthetic adversaries;
   # residual score >=.80 for every adversary and one-domain compromise.
   robust=np.vstack([w[z]*(1-dom[j]) for z in range(3) for j in range(d)])
   M=np.vstack([w,F,robust,privacy]);lb=np.r_[np.repeat(-np.log(.05),3),[1,1],np.repeat(-np.log(.2),3*d),-np.inf];ub=np.r_[np.repeat(np.inf,len(lb)-1),.65*privacy.sum()]
   # warm-up is not included in records
   if not records: solve(b,M,lb,ub)
   ex,xe,te=solve(b,M,lb,ub)
   # feasibility initialization: use full pool when feasible; otherwise feasibility MILP
   t=time.perf_counter();xh=np.ones(n);init_status=0
   if not (np.all(M@xh>=lb-1e-7) and np.all(M@xh<=ub+1e-7)):
    init,xh,_=solve(b,M,lb,ub,False);init_status=init.status
   if xh is not None:
    for i in sorted(np.flatnonzero(xh),key=lambda i:(-b[i],i)):
     y=xh.copy();y[i]=0
     if np.all(M@y>=lb-1e-7) and np.all(M@y<=ub+1e-7):xh=y
   th=time.perf_counter()-t
   # exact nominal-only ablation: same candidate pool/functions/privacy, omits residual rows
   Mn=np.vstack([w,F,privacy]);ln=np.r_[np.repeat(-np.log(.05),3),[1,1],-np.inf];un=np.r_[np.repeat(np.inf,5),.65*privacy.sum()]
   na,xn,tn=solve(b,Mn,ln,un)
   failure=None if xn is None else bool(np.any(robust@xn < -np.log(.2)-1e-7))
   rec=dict(n=n,shape=shape,rep=rep,exact_status=int(ex.status),exact_ms=te*1000,heuristic_ms=th*1000,nominal_ms=tn*1000,init_status=int(init_status),exact_cost=None if xe is None else float(b@xe),heuristic_cost=None if xh is None else float(b@xh),nominal_cost=None if xn is None else float(b@xn),nominal_fails_robust=failure)
   rec['gap_pct']=None if ex.status!=0 or xe is None or xh is None else 100*(b@xh-b@xe)/(b@xe)
   if xe is not None:assert np.all(M@xe>=lb-1e-6) and np.all(M@xe<=ub+1e-6)
   if xh is not None:
    assert np.all(M@xh>=lb-1e-6) and np.all(M@xh<=ub+1e-6)
    for i in np.flatnonzero(xh):
     y=xh.copy();y[i]=0;assert not (np.all(M@y>=lb-1e-7) and np.all(M@y<=ub+1e-7))
   records.append(rec);instances.append(dict(n=n,shape=shape,rep=rep,a=a.tolist(),burden=b.tolist(),privacy=privacy.tolist(),domains=dom.astype(int).tolist()))
with open(OUT/'benchmark_results.csv','w') as f:
 wr=csv.DictWriter(f,fieldnames=records[0].keys());wr.writeheader();wr.writerows(records)
summary=[]
for n in [10,20,30]:
 for shape in ['separate','clustered','overlap']:
  rr=[r for r in records if r['n']==n and r['shape']==shape];g=[r['gap_pct'] for r in rr if r['gap_pct'] is not None];valid=[r for r in rr if r['nominal_fails_robust'] is not None]
  summary.append(dict(n=n,shape=shape,total=len(rr),optimal=sum(r['exact_status']==0 for r in rr),infeasible=sum(r['exact_status']==2 for r in rr),time_limit=sum(r['exact_status']==1 for r in rr),exact_median_ms=float(np.median([r['exact_ms'] for r in rr])),heuristic_median_ms=float(np.median([r['heuristic_ms'] for r in rr])),gap_median=None if not g else float(np.median(g)),gap_max=None if not g else max(g),nominal_violations=sum(r['nominal_fails_robust'] for r in valid),nominal_count=len(valid)))
json.dump(dict(seed=SEED,repetitions=REPS,python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,machine=platform.machine(),processor=platform.processor(),summary=summary),open(OUT/'benchmark_summary.json','w'),indent=2)
json.dump(instances,open(OUT/'benchmark_instances.json','w'))
print(json.dumps(summary,indent=2))
