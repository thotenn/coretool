#!/bin/bash
git add .
git commit -m "reestructuring"
git push
python3 -m build
python3 -m twine upload dist/*