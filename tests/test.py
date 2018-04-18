import numpy as np
from scipy.optimize import linear_sum_assignment

cost = np.random.randint(1, 10, size=(20, 20))
cost *= -1
row_ind, col_ind = linear_sum_assignment(cost)
print "Satisfaction ", cost[row_ind, col_ind].sum() * -1 / 200.0 * 100, "%"
print "user ", row_ind+1
print "task ", col_ind+1
