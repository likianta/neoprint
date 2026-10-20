
Conceptual code:

```
import neoprint as np
from neoprint import termshot

with np.termshot() as writer:
    writer.title(
        'Comparison between Color ON:OFF \nwith syntax highlighting in IPython'
    )
    writer.input('python')
    ...
```
