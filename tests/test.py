import numpy as np
from scipy.optimize import linear_sum_assignment


cost = np.random.randint(1, 10, size=(1000, 1000))
cost *= -1
row_ind, col_ind = linear_sum_assignment(cost)
print cost[row_ind, col_ind].sum() * -1
print row_ind, col_ind