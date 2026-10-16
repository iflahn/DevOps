from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
P=Path(__file__).resolve().parent
plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none'})
def base(w,h):
 fig,ax=plt.subplots(figsize=(w,h));ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off');fig.subplots_adjust(0,0,1,1);return fig,ax
def box(ax,x,y,w,h,text,fs=10,fill='#f2f5f8'):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.008',lw=.8,ec='#3d5266',fc=fill));ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=fs)
def arrow(ax,a,b):ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=11,lw=.85,color='#3d5266'))
def save(fig,n):
 fig.savefig(P/f'figure{n}.svg');fig.savefig(P/f'figure{n}.png',dpi=450);plt.close(fig)
f,a=base(6.5,3.7)
box(a,.25,.8,.5,.14,'Requester and requested action',11)
box(a,.25,.56,.5,.14,'Authentication\nIdentity claim and credential proof',10)
box(a,.25,.28,.5,.18,'Authorization\nResource scope and household relationship\nCurrent lifecycle state and policy context',10)
arrow(a,(.5,.8),(.5,.7));arrow(a,(.5,.56),(.5,.46))
box(a,.12,.03,.3,.12,'Permit within scope',10,'#e9f1e8');box(a,.58,.03,.3,.12,'Deny or escalate',10,'#f4eae8');arrow(a,(.42,.28),(.27,.15));arrow(a,(.58,.28),(.73,.15));save(f,3)
f,a=base(6.5,4.6)
left=['Source and provenance','Dynamism and freshness','Sensitivity','Decision relevance','Management burden','Compromise dependency','Placement suitability']
right=['Decision assurance','Privacy exposure','Performance and resource cost','Freshness and lifecycle correctness','Management complexity']
for i,s in enumerate(left):
 y=.87-i*.125;box(a,.015,y,.31,.085,s,9);arrow(a,(.325,y+.04),(.405,.5))
box(a,.415,.39,.16,.21,'Parameter\nImpact\nModel',10,'#dde7f0')
for i,s in enumerate(right):
 y=.8-i*.165;box(a,.665,y,.32,.11,s if len(s)<30 else s.replace(' and ',' and\n'),9);arrow(a,(.58,.5),(.66,y+.055))
save(f,6)
f,a=base(6.5,4.6)
steps=[('Define the decision','Requester, resource, action and policy'),('Characterize candidate evidence','Seven dimensions and attack scenarios'),('Enforce admissibility and gates','Privacy, freshness, provenance and function coverage'),('Select evidence','Exact optimization or feasible reverse deletion'),('Check every required attack scenario','Residual support, functions and gate trust'),('Assign representations and tiers','Local, edge, protected storage or shared status')]
for i,(title,sub) in enumerate(steps):
 y=.84-i*.16;box(a,.15,y,.7,.12,title+'\n'+sub,9)
 if i<5:arrow(a,(.5,y),(.5,y-.04))
a.text(.02,.48,'Revise policy\nor evidence\nif infeasible',rotation=90,ha='center',va='center',fontsize=8)
save(f,7)
