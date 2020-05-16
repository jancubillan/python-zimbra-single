python-zimbra-single
====================

This Python 3 script automates the process of installing single-server Zimbra Open Source Edition v8.8.15 on CentOS 7

Requirements
------------

1) Must be a fresh CentOS 7 minimal installation
2) Static network configuration must be already set
3) Python 3 present on the server where Zimbra will be installed

How to use:
-----------
Clone and change directory to the project folder

    # git clone https://github.com/jancubillan/python-zimbra-single.git
    # cd python-zimbra-single

Modify the variables file then run tha main.py script

    # vi vars/main.py
    # python3 main.py

Reset Administrator password:

    # zmprov sp admin@example.com mypassword

License
-------

MIT License

Author Information
------------------

Author: Jan Cubillan<br/>
GitHub: https://github.com/jancubillan<br/>
