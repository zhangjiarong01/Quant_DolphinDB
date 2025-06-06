import numpy as np
from pypfopt import EfficientFrontier
import cvxpy as cp
import matplotlib.pyplot as plt
from pypfopt import objective_functions

# 原始收益与协方差估计
mu = np.array([0.03, 0.06, 0.09])
Sigma = np.array([
    [0.01, 0.0, 0.0],
    [0.0, 0.04, 0.01],
    [0.0, 0.01, 0.03]
])


# Markowitz 最优组合（最大夏普）
ef = EfficientFrontier(mu, Sigma, weight_bounds=(0, 1))
ef.add_objective(objective_functions.L2_reg, gamma=0)
w_mvo = ef.max_sharpe()
weights_mvo = ef.clean_weights()
print("最大夏普组合:", weights_mvo)

# 模拟：把股票的预期收益从 12% 改为 12.5%
mu_modified = np.array([0.035, 0.06, 0.09])

ef_mod = EfficientFrontier(mu_modified, Sigma, weight_bounds=(0, 1))
ef_mod.max_sharpe()
weights_mod = ef_mod.clean_weights()
print("轻微误差后的MVO组合:", weights_mod)