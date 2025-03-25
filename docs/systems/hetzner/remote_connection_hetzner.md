# How to remotely connect to Hetzner cloud server

- you need to copy the public key and private key from the server
- We can utilize [TFCloud](../utils/terraform/TFCloud.py) class
- you can run ```TFCloudCustom.py copy_ssh_key``` (check first the function, may need some modifications)
- After you've copied the keys, you can access the remote server.
- For instance, in VSCode:
    - in your VSCode settings, set "search.followsymlink" to false (if not set, this can cause your cpu to throttle after connecting to server)
    - go to remote explorer
    - define ssh connection by ```ssh root@<ip4-address of hetz server> -i <path to ssh key in your local computer>```
    - Open the connection
    - If throws error, check that ssh config file is set correctly for the remote server. Especially the "IdentityFile" path needs to be correct
