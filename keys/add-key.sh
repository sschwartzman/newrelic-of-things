cd ~
mkdir .ssh
chmod 700 .ssh
cd .ssh
touch authorized_keys
chmod 600 authorized_keys
cat ~/New-Relic-of-Things/keys/id_rsa.pub >> authorized_keys
