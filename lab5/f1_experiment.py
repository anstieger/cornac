"""Lab 5 - Functionality 1: Cornac README quick-start experiment."""
import platform, numpy, cornac
from cornac.eval_methods import RatioSplit
from cornac.models import MF, PMF, BPR
from cornac.metrics import MAE, RMSE, Precision, Recall, NDCG, AUC, MAP

print("python", platform.python_version(), "| cornac", cornac.__version__, "| numpy", numpy.__version__)

ml_100k = cornac.datasets.movielens.load_feedback(variant="100K")
rs = RatioSplit(data=ml_100k, test_size=0.2, rating_threshold=4.0, seed=123)

mf = MF(k=10, max_iter=25, learning_rate=0.01, lambda_reg=0.02, use_bias=True, seed=123)
pmf = PMF(k=10, max_iter=100, learning_rate=0.001, lambda_reg=0.001, seed=123)
bpr = BPR(k=10, max_iter=200, learning_rate=0.001, lambda_reg=0.01, seed=123)

metrics = [MAE(), RMSE(), Precision(k=10), Recall(k=10), NDCG(k=10), AUC(), MAP()]
cornac.Experiment(eval_method=rs, models=[mf, pmf, bpr], metrics=metrics, user_based=True).run()
