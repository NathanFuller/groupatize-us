import numpy as np
from scipy.optimize import linear_sum_assignment

<<<<<<< HEAD

cost = np.random.randint(1, 10, size=(1000, 1000))
cost *= -1
row_ind, col_ind = linear_sum_assignment(cost)
print cost[row_ind, col_ind].sum() * -1
print row_ind, col_ind
=======
cost = np.random.randint(1, 10, size=(20, 20))
cost *= -1
row_ind, col_ind = linear_sum_assignment(cost)
print "Satisfaction ", cost[row_ind, col_ind].sum() * -1 / 200.0 * 100, "%"
print "user ", row_ind+1
print "task ", col_ind+1
>>>>>>> 834a0b6eaa92651c81ff295d26bf022519ebae64
