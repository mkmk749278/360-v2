import numpy as np
import m15y as M
from sim import stats, fmt
from feat import ema
T,N=M.C.shape; liq=M.LIQ
idx=np.cumprod(1+np.nan_to_num(M.ALT)/100); e=ema(idx[:,None].astype(float),1920)[:,0]
bear=(idx<e)&(e<np.roll(e,96)); bull=(idx>e)&(e>np.roll(e,96))
band=0.0035
def mvrtp(side, a, b, regime=None):
    tr=[]; busy={}
    for t in range(max(a,2000),b):
        if regime is not None and not regime[t]: continue
        s7,s25,s99,c,pl,ph,pc=M.S7[t],M.S25[t],M.S99[t],M.C[t],M.L[t-1],M.H[t-1],M.C[t-1]
        sep=np.abs(s7-s99)/s99>=0.03
        if side>0:
            fast=(pl<=s7*(1+band))&(c>s7)&(c>pc); deep=(pl<=s25*(1+band))&(c>s25)&(c>pc); base=liq[t]&sep&(s25>s99)
        else:
            fast=(ph>=s7*(1-band))&(c<s7)&(c<pc); deep=(ph>=s25*(1-band))&(c<s25)&(c<pc); base=liq[t]&sep&(s25<s99)
        for j in np.where(np.nan_to_num(base&(fast|deep)).astype(bool))[0]:
            if busy.get(j,-1)>=t: continue
            buf=0.5*M.ATR[t,j]
            sl=((min(s25[j],pl[j]) if fast[j] else min(s99[j],pl[j]))-buf) if side>0 else ((max(s25[j],ph[j]) if fast[j] else max(s99[j],ph[j]))+buf)
            ent=float(c[j])
            if not(np.isfinite(ent) and np.isfinite(sl)) or (sl-ent)*side>=0: continue
            r=abs(ent-sl); pct,k,why=M.walk(side,t,j,ent,sl,[ent+side*r,ent+side*1.6*r],192,'ladder')
            tr.append(dict(t=t,j=j,net=pct-0.07,risk_pct=r/ent*100,why=why,exit_t=k)); busy[j]=k
    return tr
if __name__=="__main__":
    print(f"alt-bear share {bear[2000:].mean()*100:.0f}%  bull {bull[2000:].mean()*100:.0f}%")
    for side,name in ((1,'LONG'),(-1,'SHORT')):
        for lab,(a,b) in (("IS",M.IS),("OOS",M.OOS)):
            print(fmt(stats(mvrtp(side,a,b),M.ts,f"MVRTP {name} core [{lab}]")))
            print(fmt(stats(mvrtp(side,a,b,bear),M.ts,f"   alt-BEAR only [{lab}]")))
            print(fmt(stats(mvrtp(side,a,b,bull),M.ts,f"   alt-BULL only [{lab}]")))
