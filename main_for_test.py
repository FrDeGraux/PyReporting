import matplotlib.pyplot as plt
x = [1, 2, 3, 4, 5]
y1 = [1, 2, 3, 4, 5]
y2 = [1, 4, 9, 16, 25]
y3 = [25, 16, 9, 4, 1]
plt.scatter(x, y1, s = 130, c = 'yellow', marker = '*', edgecolors = 'green')
plt.savefig('python_pretty_plot.png')

plt.show()