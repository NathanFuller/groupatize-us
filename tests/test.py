import numpy as np
from scipy.optimize import linear_sum_assignment


cost = np.array([[4, 1, 3], [2, 0, 5], [3, 2, 2]])
cost *= -1
row_ind, col_ind = linear_sum_assignment(cost)
print cost[row_ind, col_ind].sum() * -1 / 15.0 * 100
print row_ind, col_ind