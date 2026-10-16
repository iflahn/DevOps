"""Schema-derived ACL instance, not a Matter stack or measured device trace.
Source: project-chip Access Control Guide, accessed 2026-10-16.
https://project-chip.github.io/connectedhomeip-doc/guides/access-control-guide.html
"""
import json
from pathlib import Path
P=Path(__file__).resolve().parent
# Commissioning establishes administrator node 112233. A subsequent ACL grants
# node 4444 Operate privilege on cluster 6 at endpoint 1. No personal traces.
acl=[dict(fabric=1,privilege=5,authMode='CASE',subjects=[112233],targets=None),dict(fabric=1,privilege=3,authMode='CASE',subjects=[4444],targets=[dict(cluster=6,endpoint=1)])]
def permit(r):
 for e in acl:
  if r['fabric']!=e['fabric'] or r['authMode']!=e['authMode'] or r['required_privilege']>e['privilege']:continue
  if e['subjects'] and r['subject'] not in e['subjects']:continue
  if e['targets'] is None or any(all(r.get(k)==v for k,v in t.items()) for t in e['targets']):return True
 return False
requests=[dict(fabric=1,authMode='CASE',subject=4444,cluster=6,endpoint=1,required_privilege=3),dict(fabric=1,authMode='CASE',subject=5555,cluster=6,endpoint=1,required_privilege=3),dict(fabric=1,authMode='CASE',subject=4444,cluster=8,endpoint=1,required_privilege=3),dict(fabric=1,authMode='CASE',subject=4444,cluster=6,endpoint=1,required_privilege=5)]
expected=[True,False,False,False];actual=[permit(r) for r in requests];assert actual==expected
json.dump(dict(source='Matter SDK Access Control Guide',source_url='https://project-chip.github.io/connectedhomeip-doc/guides/access-control-guide.html',accessed='2026-10-16',acl=acl,requests=requests,expected=expected,actual=actual,scope='Schema-derived illustration, not a normative conformance test or execution of a Matter stack'),open(P/'matter_policy_results.json','w'),indent=2)
print('PASS: four schema-derived ACL requests give expected permit/deny outcomes.')
