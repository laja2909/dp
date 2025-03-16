# Instructions for generating ssh key
- run ```ssh-keygen -t ed25519 -C "your_email@example.com"```
    - it will ask you to define file names and entering passphrase
    - hit enter if you want to keep the file name as default
    - set passphrase
    - two files are created: private key file and public key file
    - open public key file and copy the content to clipboard
    - go to your hetzner project and under security "Add SSH key"
    - copy the content of your public to the text field and give name to the key
    - Create the key