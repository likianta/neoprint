import neoprint as np

data = {
    'users': [
        {'name': 'Alice', 'tags': ['dev', 'ops']},
        {'name': 'Bob', 'tags': ['design']},
    ]
}
np.show(data, ':l')