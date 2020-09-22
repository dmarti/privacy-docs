#!/usr/bin/bash

FROM=$(egrep '^set from' $HOME/.muttrc | cut -d '=' -f 2 | tr -d '"')

if [ "x$CCPA_EMAIL" == 'x' ]; then
        export CCPA_EMAIL=$FROM
fi

EARTHLY_SECRETS="name=$CCPA_NAME,addressblock=$CCPA_ADDRESSBLOCK,ccpa_agent_name=$CCPA_AGENT_NAME" \
earth +build 

