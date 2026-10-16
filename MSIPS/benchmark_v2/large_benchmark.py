"""MSIPS v2 stress benchmark. Generated, not observed smart-home traces.
Run python large_benchmark.py. Requires numpy/scipy. Timings are host-dependent.
"""
import os
os.environ.setdefault('OMP_NUM_THREADS','1')
import numpy as np, scipy, json,csv,time,platform
from scipy.optimize import milp,linprog,Bounds,LinearConstraint
from pathlib import Path
P=Path(__file__).resolve().parent
SEED=2026101602; rng=np.random.default_rng(SEED); REPS=3
EXACT_LIMIT=3.; START_LIMIT=1.; SWAP_LIMIT=600
allrows=[]; instances=[]
def solve(c,M,lb,budget,pr,limit,integer=True):
 mat=np.vstack([M,pr]);lo=np.r_[lb,-np.inf];up=np.r_[np.repeat(np.inf,len(lb)),budget]
 st=time.perf_counter();r=milp(c,integrality=np.ones(len(c)) if integer else np.zeros(len(c)),bounds=Bounds(0,1),constraints=LinearConstraint(mat,lo,up),options={'time_limit':limit,'mip_rel_gap':0.0});dt=time.perf_counter()-st
 x=None if r.x is None else (r.x>.5).astype(float)
 return r,x,dt

def feasible(x,M,lb,pr,B):return x is not None and pr@x<=B+1e-7 and np.all(M@x>=lb-1e-7)
def prune(x,c,M,lb,pr,B):
 if not feasible(x,M,lb,pr,B):return None
 x=x.copy()
 for i in sorted(np.flatnonzero(x),key=lambda i:(-c[i],i)):
  y=x.copy();y[i]=0
  if feasible(y,M,lb,pr,B):x=y
 return x

def forward(c,M,lb,pr,B,eta):
 n=len(c);x=np.zeros(n);v=np.zeros(len(lb))
 # gain is the sum of clipped normalized deficits reduced by this item.
 norm=M/lb[:,None]
 for _ in range(n):
  if np.all(v>=lb-1e-7):return x
  deficit=np.maximum(0,1-v/lb)
  gain=np.minimum(norm,deficit[:,None]).sum(axis=0)
  score=gain/(c+eta*pr)
  score[(x>0)|(pr@x+pr>B+1e-7)]=-np.inf
  j=int(np.argmax(score))
  if not np.isfinite(score[j]) or score[j]<=1e-12:return None
  x[j]=1;v+=M[:,j]
 return x if feasible(x,M,lb,pr,B) else None

def local(x,c,M,lb,pr,B):
 x=prune(x,c,M,lb,pr,B)
 if x is None:return None,0
 tests=0
 # bounded first-improvement one-for-one exchange followed by reverse deletion.
 while tests<SWAP_LIMIT:
  improved=False
  for i in sorted(np.flatnonzero(x),key=lambda i:(-c[i],i)):
   candidates=sorted(np.flatnonzero((x==0)&(c<c[i])),key=lambda j:(c[j],j))
   v=M@x-M[:,i];px=pr@x-pr[i]
   for j in candidates:
    tests+=1
    if px+pr[j]<=B+1e-7 and np.all(v+M[:,j]>=lb-1e-7):
     x[i]=0;x[j]=1;x=prune(x,c,M,lb,pr,B);improved=True;break
    if tests>=SWAP_LIMIT:break
   if improved or tests>=SWAP_LIMIT:break
  if not improved:break
 return x,tests
# discarded warm-up
milp(np.ones(2),integrality=np.ones(2),bounds=Bounds(0,1),constraints=LinearConstraint([[1,1]],1,np.inf))
for n in [100,300,1000]:
 for shape in ['clustered','correlated_overlap']:
  for factor in [1.05,1.25]:
   for rep in range(REPS):
    ident=f'n{n}_{shape}_b{factor}_{rep}';d={100:10,300:20,1000:30}[n]
    group=rng.integers(0,d,n);dom=np.zeros((d,n))
    for i,g in enumerate(group):
     dom[g,i]=1
     if shape=='correlated_overlap':dom[(g+1)%d,i]=1
    # Contributions share latent domain and item components across adversaries.
    latent=rng.uniform(.04,.18,d);item=rng.uniform(.75,1.25,n)
    a=np.clip(np.vstack([latent[group]*item*rng.uniform(.7,1.3,n) for _ in range(3)]),.015,.3)
    # Two attack-specific weak groups in each scenario.
    for t in range(3):a[t,np.isin(group,[(2*t)%d,(2*t+1)%d])]*=.2
    w=-np.log1p(-a);c=rng.integers(1,21,n).astype(float);pr=rng.integers(1,11,n).astype(float)
    F=np.zeros((4,n))
    for i in range(n):F[i%4,i]=1
    robust=np.vstack([w[t]*(1-dom[j]) for t in range(3) for j in range(d)])
    # Residual authentication function (group 0) under each domain compromise.
    auth=np.vstack([F[0]*(1-dom[j]) for j in range(d)])
    M=np.vstack([w,F,robust,auth]);lb=np.r_[np.repeat(-np.log(.01),3),np.ones(4),np.repeat(-np.log(.05),3*d),np.ones(d)]
    # LP privacy lower bound, before adding the privacy budget.
    lp=linprog(pr,A_ub=-M,b_ub=-lb,bounds=(0,1),method='highs');assert lp.success
    B=float(factor*lp.fun)
    exact,xe,te=solve(c,M,lb,B,pr,EXACT_LIMIT)
    # Nominal ablation remains a sanity check only.
    Mn=np.vstack([w,F]);ln=np.r_[np.repeat(-np.log(.01),3),np.ones(4)]
    nom,xn,tn=solve(c,Mn,ln,B,pr,START_LIMIT)
    violated=None if xn is None else not feasible(xn,M,lb,pr,B)
    # Main comparator uses no MILP seed. Failed construction is not infeasibility.
    st=time.perf_counter();starts=[forward(c,M,lb,pr,B,e) for e in [0.,2.,10.,100.,100000.]];starts=[x for x in starts if x is not None];fg=min(starts,key=lambda x:float(c@x)) if starts else None;xf,swaps=local(fg,c,M,lb,pr,B);tf=time.perf_counter()-st
    # Paired initialization experiment, same reverse-delete pass, different starts.
    seeds={};init_times={}
    for eta in [10.,100.]:
     st=time.perf_counter();z=forward(c,M,lb,pr,B,eta);seeds[f'greedy_eta{eta:g}']=prune(z,c,M,lb,pr,B);init_times[f'greedy_eta{eta:g}']=time.perf_counter()-st
    st=time.perf_counter();rs,z,_=solve(np.zeros(n),M,lb,B,pr,START_LIMIT);seeds['milp_feasibility']=prune(z,c,M,lb,pr,B);init_times['milp_feasibility']=time.perf_counter()-st
    lbnd=float(exact.mip_dual_bound) if getattr(exact,'mip_dual_bound',None) is not None else None
    best=None if xe is None else float(c@xe)
    for alg,x,dt in [('forward_local',xf,tf),*[(k,seeds[k],init_times[k]) for k in seeds]]:
     if x is not None:assert feasible(x,M,lb,pr,B)
     cost=None if x is None else float(c@x)
     allrows.append(dict(instance=ident,n=n,shape=shape,budget_factor=factor,rep=rep,algorithm=alg,exact_status=int(exact.status),exact_ms=te*1000,exact_incumbent=best,exact_lower_bound=lbnd,exact_mip_gap=None if getattr(exact,'mip_gap',None) is None else float(exact.mip_gap),heuristic_success=x is not None,heuristic_ms=dt*1000,heuristic_cost=cost,gap_to_opt_pct=None if exact.status!=0 or cost is None or best is None else 100*(cost-best)/best,gap_to_bound_pct=None if cost is None or lbnd is None or lbnd<=0 else 100*(cost-lbnd)/lbnd,nominal_fails_robust=violated,nominal_status=int(nom.status),swap_tests=swaps if alg=='forward_local' else 0))
    instances.append(dict(id=ident,n=n,shape=shape,budget_factor=factor,a=a.tolist(),cost=c.tolist(),privacy=pr.tolist(),budget=B,lp_privacy=float(lp.fun),domains=dom.astype(int).tolist(),selected_exact=None if xe is None else np.flatnonzero(xe).tolist(),selected_forward=None if xf is None else np.flatnonzero(xf).tolist()))
    print(ident,'status',exact.status,'exact',best,'FG',None if xf is None else float(c@xf),flush=True)
with open(P/'large_results.csv','w') as f:
 wr=csv.DictWriter(f,fieldnames=allrows[0].keys());wr.writeheader();wr.writerows(allrows)
json.dump(instances,open(P/'large_instances.json','w'))
summary=[]
for n in [100,300,1000]:
 for factor in [1.05,1.25]:
  rr=[r for r in allrows if r['algorithm']=='forward_local' and r['n']==n and r['budget_factor']==factor];gg=[r['gap_to_opt_pct'] for r in rr if r['gap_to_opt_pct'] is not None];bb=[r['gap_to_bound_pct'] for r in rr if r['gap_to_bound_pct'] is not None];success=[r for r in rr if r['heuristic_success']]
  summary.append(dict(n=n,budget_factor=factor,total=len(rr),optimal=sum(r['exact_status']==0 for r in rr),limited=sum(r['exact_status']==1 for r in rr),infeasible=sum(r['exact_status']==2 for r in rr),exact_median_ms=float(np.median([r['exact_ms'] for r in rr])),fg_success=len(success),fg_median_ms=float(np.median([r['heuristic_ms'] for r in rr])),gap_opt_median=None if not gg else float(np.median(gg)),gap_opt_n=len(gg),gap_bound_median=None if not bb else float(np.median(bb))))
paired=[]
for ins in instances:
 rr=[r for r in allrows if r['instance']==ins['id'] and r['algorithm']!='forward_local'];costs=[r['heuristic_cost'] for r in rr if r['heuristic_cost'] is not None]
 paired.append(dict(instance=ins['id'],successful_seeds=len(costs),best=None if not costs else min(costs),worst=None if not costs else max(costs),spread_pct=None if len(costs)<2 else 100*(max(costs)-min(costs))/min(costs)))
json.dump(dict(seed=SEED,replicates=REPS,exact_limit_s=EXACT_LIMIT,start_limit_s=START_LIMIT,swap_limit=SWAP_LIMIT,python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,summary=summary,initialization=paired),open(P/'large_summary.json','w'),indent=2)
print(json.dumps(summary,indent=2))
