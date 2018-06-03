import os

egg = 'dist'

if os.path.exists(egg):
    for f in os.listdir(egg):
        os.remove(os.path.join(egg, f))

os.system('python setup.py sdist')
os.system('twine upload dist/*')
