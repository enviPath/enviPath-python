# enviPath Python

Python client for [enviPath](https://envipath.org) - the environmental contaminant biotransformation pathway resource.

## Quickstart

```bash
pip install --upgrade enviPath-python
```

```python
from pprint import pprint
from enviPath_python import enviPath

eP = enviPath('https://envipath.org')

bbd = eP.get_package('https://envipath.org/package/32de3cf4-e3e6-4168-956e-32fa5ddb0ce1')

bbd_pws = bbd.get_pathways()

pprint(bbd_pws[0].get_description())
```

## Documentation

The enviPath-python documentation can be found [here](https://envipath-python.readthedocs.io/en/feature-docs/).

If you are new to enviPath [our wiki](https://wiki.envipath.org/index.php/Main_Page) might also contain some value
information.

## Examples

### Accessing Data

```python
from pprint import pprint
from enviPath_python import enviPath

eP = enviPath('https://envipath.org')

# get the EAWAG BBD package
bbd = eP.get_package('https://envipath.org/package/32de3cf4-e3e6-4168-956e-32fa5ddb0ce1')

# access collections (e.g. compounds)
# other collections such as reactions, rules, pathways, etc work the same way
compounds = bbd.get_compounds()

for c in compounds[:10]:
    print(c.get_id(), c.get_name(), c.get_smiles())

```

### Accessing private data

```python
import getpass
from enviPath_python import enviPath

eP = enviPath('https://envipath.org')

# get username + password
username = input("Enter username")
password = getpass.getpass(prompt="Password for {}".format(username))
eP.login(username, password)

print(eP.who_am_i())

for p in eP.get_packages()[:10]:
    print(p)
```

### Predict Pathways

```python
from enviPath_python import enviPath
from enviPath_python.objects import Pathway
from time import sleep

eP = enviPath('https://envipath.org')

# obtain the currently logged in user
me = eP.who_am_i()

# get the package the pathway should be stored in
package = me.get_default_package()

# will trigger the pathway prediction
pw = Pathway.create(package, smiles='CC1(C)C2CCC1(C)C(=O)C2')

# wait until the prediction finished
while pw.is_running():
    print("Sleeping for three secs...")
    sleep(3)

# check result
if pw.has_failed():
    exit(1)
else:
    for node in pw.get_nodes():
        print(node.get_smiles())
```