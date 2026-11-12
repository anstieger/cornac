"""Lab 5 - Functionality 2: top-K recommendations for one user vs. held-out ground truth."""
import numpy as np, cornac
from cornac.eval_methods import RatioSplit
from cornac.models import BPR

K = 10
data = cornac.datasets.movielens.load_feedback(variant="100K")
rs = RatioSplit(data=data, test_size=0.2, rating_threshold=4.0, seed=123, exclude_unknowns=True)
bpr = BPR(k=10, max_iter=200, learning_rate=0.001, lambda_reg=0.01, seed=123).fit(rs.train_set)

train, test = rs.train_set, rs.test_set
uid_map, iid_map = train.uid_map, train.iid_map
idx2iid = {v: k for k, v in iid_map.items()}

# pick the first test user who has >= 5 relevant (rating >= 4) held-out items
for raw_uid, uidx in uid_map.items():
    if uidx not in test.user_indices:
        continue
    rows = [(i, r) for u, i, r in zip(test.uir_tuple[0], test.uir_tuple[1], test.uir_tuple[2]) if u == uidx]
    relevant = {idx2iid[i] for i, r in rows if r >= 4.0}
    if len(relevant) >= 5:
        break

scores = bpr.score(uidx)
seen = set(train.matrix[uidx].indices)          # don't recommend training items
ranked = [i for i in np.argsort(-scores) if i not in seen][:K]
top_k = [idx2iid[i] for i in ranked]
hits = [i for i in top_k if i in relevant]

print(f"user {raw_uid}: {len(relevant)} relevant held-out items")
print(f"top-{K}:", top_k)
print(f"hits: {hits}  ->  precision@{K} = {len(hits)/K:.2f}")
