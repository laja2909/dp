# Instructions for generating ssh key
- run ```ssh-keygen -t ed25519 -C "your_email@example.com"```
    - it will ask you to define file names and entering passphrase
    - hit enter if you want to keep the file name as default
    - set passphrase
    - two files are created: private key file and public key file
    - Save them to secure location
    - go to setup/variable.tf and specify sshkey public key filename to variables called  ```ssh_public_name```
    - add the file path as environment variable to your local computer. Use variable name ```TF_VAR_ssh_path```
    