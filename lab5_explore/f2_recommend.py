"""Lab 5 - Functionality 2: top-K recommendations for one user vs. held-out ground truth.
Uses the public Recommender.recommend() API (original user/item IDs)."""
import cornac
from cornac.eval_methods import RatioSplit
from cornac.models import BPR

K = 10
data = cornac.datasets.movielens.load_feedback(variant="100K")
rs = RatioSplit(data=data, test_size=0.2, rating_threshold=4.0, seed=123,
                exclude_unknowns=True, verbose=False)
bpr = BPR(k=10, max_iter=200, learning_rate=0.001, lambda_reg=0.01, seed=123).fit(rs.train_set)

test = rs.test_set
idx2iid = {idx: raw for raw, idx in test.iid_map.items()}

# first test user with >= 5 relevant (rating >= 4) held-out items
for raw_uid, uidx in test.uid_map.items():
    items, ratings = test.user_data.get(uidx, ([], []))
    relevant = {idx2iid[i] for i, r in zip(items, ratings) if r >= 4.0}
    if len(relevant) >= 5 and raw_uid in bpr.uid_map:
        break

top_k = bpr.recommend(raw_uid, k=K, remove_seen=True, train_set=rs.train_set)
hits = [i for i in top_k if i in relevant]

print(f"user {raw_uid}: {len(relevant)} relevant held-out items (rating >= 4)")
print(f"top-{K} recommended item IDs: {top_k}")
print(f"hits: {hits}  ->  precision@{K} = {len(hits)/K:.2f}, recall@{K} = {len(hits)/len(relevant):.2f}")
