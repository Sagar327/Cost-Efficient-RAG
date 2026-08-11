import json, math, statistics, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.rag import retrieve

def relevant(item, q):
    source_ok = item["source"] in q["relevant_sources"]
    kw = q.get("relevant_keywords", [])
    text = item["text"].lower()
    return source_ok and (not kw or any(k.lower() in text for k in kw))

def dcg(rels):
    return sum((2**r-1)/math.log2(i+2) for i,r in enumerate(rels))

def main(k=5):
    qs=json.loads(Path("eval/questions.json").read_text())
    rows=[]
    for q in qs:
        hits=retrieve(q["question"], k)
        rel=[1 if relevant(x,q) else 0 for x in hits]
        ranks=[i+1 for i,r in enumerate(rel) if r]
        recall=1.0 if ranks else 0.0  # one or more gold chunks is sufficient for these questions
        hit=recall
        mrr=1/ranks[0] if ranks else 0.0
        ideal=[1] + [0]*(k-1)
        ndcg=dcg(rel)/dcg(ideal) if dcg(ideal) else 0
        precision=sum(rel)/len(rel) if rel else 0
        rows.append((q["id"],recall,hit,mrr,ndcg,precision))
    cols=["id","recall_at_k","hit_rate","mrr","ndcg","context_precision"]
    print(",".join(cols))
    for r in rows: print(",".join(f"{x:.4f}" if isinstance(x,float) else str(x) for x in r))
    print("\nMEAN")
    for i,c in enumerate(cols[1:],1): print(c, round(statistics.mean(r[i] for r in rows),4))

if __name__=="__main__":
    main(int(sys.argv[1]) if len(sys.argv)>1 else 5)
