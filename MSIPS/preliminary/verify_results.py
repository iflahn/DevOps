"""Independent exhaustive oracle for all 60 ten-item instances."""
import json,csv,itertools,numpy as np
from pathlib import Path
P=Path(__file__).resolve().parent
instances=json.load(open(P/'benchmark_instances.json'));rows=list(csv.DictReader(open(P/'benchmark_results.csv')))
for ins,row in zip(instances,rows):
 if ins['n']!=10:continue
 n=10;w=-np.log1p(-np.array(ins['a']));b=np.array(ins['burden']);privacy=np.array(ins['privacy']);dom=np.array(ins['domains']);best=float('inf')
 for bits in itertools.product([0,1],repeat=n):
  x=np.array(bits)
  if not x[:5].any() or not x[5:].any() or privacy@x>.65*privacy.sum()+1e-8:continue
  if np.any(w@x < -np.log(.05)-1e-8):continue
  if any(np.any((w*(1-d))@x < -np.log(.2)-1e-8) for d in dom):continue
  best=min(best,b@x)
 if np.isinf(best):assert row['exact_status']=='2'
 else:assert row['exact_status']=='0' and abs(float(row['exact_cost'])-best)<1e-8
print('PASS: all 60 ten-item MILP results agree with exhaustive enumeration.')
