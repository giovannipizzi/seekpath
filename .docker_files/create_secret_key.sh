#!/bin/bash
## Generate the secret key (but only once, don't overwrite if existsing

function gen_pwd_char() {
    s=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890-_%/
    # Length of the string
    p=$(( $RANDOM % 66))
    echo -n ${s:$p:1}
}

SECRET_KEY_FILE=/home/app/code/seekpath/webservice/SECRET_KEY
if [ ! -e "$SECRET_KEY_FILE" ]
then

   #16-char pwd
   NEW_PASSWORD=`gen_pwd_char; gen_pwd_char; gen_pwd_char; gen_pwd_char; gen_pwd_char; gen_pwd_char; gen_pwd_char; gen_pwd_char; gen_pwd_char; gen_pwd_char; gen_pwd_char; gen_pwd_char; gen_pwd_char; gen_pwd_char; gen_pwd_char; gen_pwd_char; `

   echo "$NEW_PASSWORD" > "$SECRET_KEY_FILE"
   chown app:app "$SECRET_KEY_FILE"
   chmod 600 "$SECRET_KEY_FILE"
   
fi