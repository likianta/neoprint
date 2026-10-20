import neoprint as np

name = 'Alice'
age = 30
city = 'New York'
np.show(name, age, city, ':n')

names = ['Alice', 'Bob']
np.show(len(names), ':n')

class Box:
    def __init__(self):
        self.value = 42

box = Box()
np.show(box.value, ':n')