# Compile (takes a while!)

This is obsolete - since the raspian - aka debian buster - now has python 3.7.3 pre-intalled.
This is obsolete - since the raspian - aka debian buster - now has python 3.7.3 pre-intalled.
This is obsolete - since the raspian - aka debian buster - now has python 3.7.3 pre-intalled.
This is obsolete - since the raspian - aka debian buster - now has python 3.7.3 pre-intalled.

## https://gist.github.com/SeppPenner/6a5a30ebc8f79936fa136c524417761d

shorter

## https://www.ramoonus.nl/2018/06/30/installing-python-3-7-on-raspberry-pi/

```bash
wget https://www.python.org/ftp/python/3.7.6/Python-3.7.6.tar.xz
tar xf Python-3.7.6.tar.xz
cd Python-3.7.6
./configure --prefix=/usr/local/opt/python-3.7.6
make -j 4

# Install
sudo make altinstall

# Make Python 3.7 the default version, make aliases
sudo ln -s /usr/local/opt/python-3.7.6/bin/pydoc3.7   /usr/bin/pydoc3.7
sudo ln -s /usr/local/opt/python-3.7.6/bin/python3.7  /usr/bin/python3.7
sudo ln -s /usr/local/opt/python-3.7.6/bin/python3.7m /usr/bin/python3.7m
sudo ln -s /usr/local/opt/python-3.7.6/bin/pyvenv-3.7 /usr/bin/pyvenv-3.7
sudo ln -s /usr/local/opt/python-3.7.6/bin/pip3.7     /usr/bin/pip3.7


alias python3='/usr/bin/python3.7'
alias pip3='/usr/local/opt/python-3.7.6/bin/pip3.7'

ls /usr/bin/python*
cd ..
sudo rm -r Python-3.7.6
rm Python-3.7.6.tar.xz
. ~/.bashrc


# And if you want to revert:
update-alternatives --config python

# pbu addenum

# setting symlinks is mist
# ln -s  ZIEL LINK_NAME
ls -lAh /usr/bin/python*

sudo ln -sf /usr/local/opt/python-3.7.6/bin/pydoc3.7   /usr/bin/pydoc
sudo ln -sf /usr/local/opt/python-3.7.6/bin/python3.7  /usr/bin/python
sudo ln -sf /usr/local/opt/python-3.7.6/bin/python3.7m /usr/bin/pythonm
sudo ln -sf /usr/local/opt/python-3.7.6/bin/pyvenv-3.7 /usr/bin/pyvenv
sudo ln -sf /usr/local/opt/python-3.7.6/bin/pip3.7     /usr/bin/pip

sudo ln -sf /usr/local/opt/python-3.7.6/bin/pydoc3.7   /usr/bin/pydoc3
sudo ln -sf /usr/local/opt/python-3.7.6/bin/python3.7  /usr/bin/python3
sudo ln -sf /usr/local/opt/python-3.7.6/bin/python3.7m /usr/bin/python3m
sudo ln -sf /usr/local/opt/python-3.7.6/bin/pyvenv-3.7 /usr/bin/pyvenv-3
sudo ln -sf /usr/local/opt/python-3.7.6/bin/pip3.7     /usr/bin/pip3


# reset
sudo ln -sf pydoc2.7   /usr/bin/pydoc
sudo ln -sf python2.7  /usr/bin/python
sudo ln -sf python2.7m /usr/bin/pythonm
sudo ln -sf pyvenv-2.7 /usr/bin/pyvenv
sudo ln -sf pip2.7     /usr/bin/pip
sudo rm /usr/bin/pythonm

sudo ln -sf pydoc3.5   /usr/bin/pydoc3
sudo ln -sf python3.5  /usr/bin/python3
sudo ln -sf python3.5m /usr/bin/python3m
sudo ln -sf pyvenv-3.5 /usr/bin/pyvenv-3
sudo ln -sf pip3.5     /usr/bin/pip3


```

sudo python  -m pip install --upgrade pip
sudo python3 -m pip install --upgrade pip