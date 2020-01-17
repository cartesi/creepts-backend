#!/bin/sh

set -e

if [ -z "${ACCOUNT_ADDRESS}" ] && [ -z "${MNEMONIC}" ]; then
    # does not have mnemonic env variable, wait for keys in directory /opt/cartesi/etc/keys/
    echo "No MNEMONIC or ACCOUNT_ADDRESS defined, waiting for account file at /opt/cartesi/etc/keys/"
    dockerize -wait file://$BASE/etc/keys/keys_done -timeout ${TIMEOUT}
    export ACCOUNT_ADDRESS=$(cat /opt/cartesi/etc/keys/account)
fi

if [ -z "${MOCKED_SERVER}" ]; then
    # wait for dispatcher to be available before starting application
    dockerize -wait tcp://${DISPATCHER_HOST}:${DISPATCHER_PORT} -timeout ${DISPATCHER_TIMEOUT}

    # wait for deployment
    if [ -z "${NETWORK_ID}" ]; then
        echo "Waiting for blockchain deployment..."
        dockerize -wait file://$BASE/share/blockchain/deploy_done -timeout ${TIMEOUT}
    fi
fi

if [ -z "${ACCOUNT_ADDRESS}" ] && [ -z "${MNEMONIC}" ]; then
    echo "No ACCOUNT_ADDRESS or MNEMONIC configured"
    exit 1;
fi

$@
