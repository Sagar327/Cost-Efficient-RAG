import json, re, statistics, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.rag import answer

def words(s): return set(re.findall(r"[a-z0-9]+", s.lower()))
def keyword_f1(text, keywords):
    got=words(text); gold=set(words(" ".join(keywords)))
    if not gold: return 0.0
    p=len(got & gold)/max(1,len(got))
    r=len(got & gold)/len(gold)
    return 2*p*r/max(1e-9,p+r)

def citation_grounding(result):
    ans=result["answer"]
    cited=[int(x) for x in re.findall(r"\[(\d+)\]", ans)]
    if not cited: return 0.0
    valid=sum(1 for x in cited if 1 <= x <= len(result["contexts"]))
    return valid/len(cited)

def main():
    qs=json.loads(Path("eval/questions.json").read_text())
    scores=[]
    for q in qs:
        r=answer(q["question"], k=5)
        f1=keyword_f1(r["answer"], q["relevant_keywords"])
        grounded=citation_grounding(r)
        scores.append((f1, grounded))
        print(q["id"], f"keyword_F1={f1:.3f}", f"citation_grounding={grounded:.3f}", f"latency_ms={r['total_ms']}")
    print("MEAN keyword_F1:", round(statistics.mean(x[0] for x in scores),3))
    print("MEAN citation_grounding:", round(statistics.mean(x[1] for x in scores),3))
    print("Note: these are automated proxies. Manually inspect 5-10 answers and report limitations; do not call this a human-validated faithfulness score.")
if __name__=="__main__":
    main()
