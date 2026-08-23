"""E-C1R: rich vs plain context — same 8 episodes, one variable: context richness."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cogym.agents.model import OpenAICompatible
import collude as C, context as CX
SYMBOLS=["SPY","QQQ","TLT","GLD"]; START,END="2024-08-01","2026-08-22"; HORIZON=5; INDICES=[300,430]
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"outputs")
def main():
 m=OpenAICompatible(model_id=C.MODEL_ID,base_url=C.BASE_URL,api_key=os.environ["OPENCODE_GO_API_KEY"],timeout=300)
 eps, bank_hash=C.build_episode_bank(SYMBOLS,START,END,HORIZON,INDICES)
 from cogym.trading.alpaca.world import create_alpaca_world
 wmap={}
 for s in SYMBOLS:
  wmap[s]=create_alpaca_world(s,START,END,key_id=os.environ["ALPACA_KEY_ID"],secret_key=os.environ["ALPACA_SECRET_KEY"])
 res={"bank_hash":bank_hash,"conditions":{}}
 for cond in ["plain","rich"]:
  utils=[]
  for ep in eps:
   bars=wmap[ep.symbol].bars
   idx=next(i for i,b in enumerate(bars) if b.close==ep.price and str(b.ts.date())==ep.as_of) if False else None
   # rebuild window deterministically from bank
   win=[b for b in wmap[ep.symbol].bars if str(b.ts.date()) < ep.as_of][-60:]
   rich=CX.rich_window_text(win, vw=[getattr(b,'vw',None) for b in win]) if cond=="rich" else ""
   news="\n".join(CX.fetch_news(ep.symbol, ep.as_of)) if cond=="rich" else ""
   hourly=CX.hourly_confirmation_text(ep.symbol, ep.as_of, os.environ["ALPACA_KEY_ID"], os.environ["ALPACA_SECRET_KEY"]) if cond=="rich" else None
   extra=""
   if rich: extra+=rich+"\n"
   if news: extra+="News:\n"+news+"\n"
   if hourly: extra+="Intraday: "+hourly+"\n"
   t=C.call_subject(m,ep,C.ROLE_PROMPTS["homogeneous"],0.7,11,extra_context=extra)
   utils.append(C.score(C.parse_stance(t),ep))
  res["conditions"][cond]={"mean_utility_bps":round(sum(utils)/len(utils)*1e4,2)}
 res["V_rich_bps"]=round(res["conditions"]["rich"]["mean_utility_bps"]-res["conditions"]["plain"]["mean_utility_bps"],2)
 open(os.path.join(OUT,"ec1r-results.json"),"w").write(json.dumps(res,indent=2))
 print(json.dumps(res,indent=1))
if __name__=="__main__": main()
