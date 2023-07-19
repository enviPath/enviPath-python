# enviPath Python

## Quickstart

```python
from pprint import pprint
from enviPath_python import enviPath

eP = enviPath('https://envipath.org')

bbd = eP.get_package('https://envipath.org/package/32de3cf4-e3e6-4168-956e-32fa5ddb0ce1')

bbd_pws = bbd.get_pathways()

pprint(bbd_pws[0].get_description())
```

## Advanced

```python
from enviPath_python import enviPath
from enviPath_python.utils import NonPersistent

eP = enviPath('https://envipath.org')
np = NonPersistent(eP)

setting = eP.who_am_i().get_default_setting()

predictions = np.predict(eP.who_am_i().get_default_setting(), 'c1ccccc1')
```

