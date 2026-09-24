import os
from paths import DATA
import numpy as np
import m15y as M
from sim import stats, fmt
T,N=M.C.shape; liq=M.LIQ
TBQ=np.load(os.path.join(DATA, 'tbq15y.npy')).astype(float)
buy=TBQ/M.QV                                       # taker-buy share of the bar
HI24=np.full_like(M.H,np.nan)
for t in range(24,T): HI24[t]=np.nanmax(M.H[t-24:t],axis=0)
def trap(a,b,max_buy=None,min_sweep_vol=None,tp_r=1.5,hold=16):
    tr=[]; busy={}
    for t in range(max(a,200),b):
        lvl=HI24[t]
        m=liq[t]&(M.H[t]>lvl)&(M.C[t]<lvl)&(M.C[t]<M.O[t])
        if max_buy is not None: m&=buy[t]<=max_buy
        for j in np.where(np.nan_to_num(m).astype(bool))[0]:
            if busy.get(j,-1)>=t or t+1>=T: continue
            e=float(M.O[t+1,j]); sl=M.H[t,j]+0.25*M.ATR[t,j]
            if not(np.isfinite(e) and np.isfinite(sl)) or sl<=e*1.002 or (sl-e)/e*100>5: continue
            r=sl-e; pct,k,why=M.walk(-1,t,j,e,sl,[e-tp_r*r,e-tp_r*r],hold,'tp1')
            if not np.isfinite(pct): continue
            tr.append(dict(t=t,j=j,net=pct-0.17,risk_pct=r/e*100,why=why,exit_t=k)); busy[j]=k
    return tr
if __name__=="__main__":
    for mb in (None,0.48,0.45,0.42):
        for lab,(a,b) in (("IS",M.IS),("OOS",M.OOS)):
            print(fmt(stats(trap(a,b,max_buy=mb),M.ts,f"TRAP core buy<={mb} [{lab}]")))
