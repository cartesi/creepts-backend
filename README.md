# Creepts Backend server

This repo implements a REST API in Python that serves the [Creepts game front-end](https://github.com/cartesi/creepts-game).
The API talks to the [Creepts DApp](https://github.com/cartesi/creepts-dapp), which talks to the blockchain.

The REST API is defined in OpenAPI V3, in the directory `reference/anuto/`.
That also includes examples of each endpoint response.

## Running the server locally

## Prerequisites

- Python3 installed
- Dispatcher server from the cartesi creepts-dapp repository available
- cartesi-machine-hash tool from the cartesi machine-emulator repository available
- Available Ethereum node specified in the WEB3_PROVIDER_URI env var
- Install dependencies (preferably in a virtualenv):
```
   pip install -r requirements.txt
```
- Define some env variables that specify some information needed by the server
```
export CONTRACTS_DIR=<PATH TO THE CREEPTS DAPP DIRECTORY> #the one from the creepts-dapp repository
export ACCOUNT_ADDRESS=<ETH ADDRESS TO USE FOR THE PLAYER> #alternatively you can specify the MNEMONIC env variable with the mnemonic of the desired eth wallet
export DISPATCHER_URL=<URL OF THE DISPATCHER SERVER> #the one from the creepts-dapp repository
export PACKLOG_CMD=<COMMAND TO USE THE PACKLOG SCRIPT> #there is one in the root directory of this repo
export UNPACKLOG_CMD=<COMMAND TO USE THE UNPACKLOG SCRIPT> #there is one in the root directory of this repo
export HASH_BINARY_CMD=<COMMAND TO USE THE CARTESI MACHINE HASH TOOL> #available in the cartesi machine-emulator repository
export WEB3_PROVIDER_URI=<WITH THE URI OF THE AVAILABLE ETHEREUM NODE>
```

## Running the server

```
gunicorn creepts.app:api
```

You may also wish to run the server with the `--log-level debug` and `--preload` options when developing to help debugging

## Running the tests

```
python -m unittest discover creepts/tests
```

## Testing the dispatcher and creepts backend server API manually

There are a couple of HTTPie-based simple scripts to manually test the dispatcher and creepts backend server endpoionts.
There is also a mock dispatcher scripts that starts a mocked dispatcher that returns responses based in the static files inside the creepts/tests/instance_samples directory.
They are located inside the creepts/tests directory:
```
run_mock_dispatcher.sh #starts the mocked dispatcher
httpie_test_get_instance.sh #tool to ask for an instance in the dispatcher
httpie_test_get_instances.sh #tool to ask for the list of instances in the dispatcher

httpie_test_get_my_info.sh #tool to ask for the own player info
httpie_test_get_my_score.sh #tool to ask for the own player score and gameplay log
httpie_test_get_player_score.sh #tool to ask for any player score and gameplay log
httpie_test_get_tournament.sh #tool to ask for a specific tournament info
httpie_test_get_tournaments.sh #tool to ask for all tournaments info
httpie_test_put_my_score.sh #tool to commit a score and gameplay log for a tournament
```
## API Documentation

### Using docker

    docker run --rm -v $(pwd)/reference/anuto:/project -p 5000:5000 wework/speccy serve openapi.yaml

### Running locally

Install [speccy](http://speccy.io), then run:

    speccy serve reference/anuto/openapi.yaml

Open documentation at [http://localhost:5000/](http://localhost:5000/)

### Validation

To validate the spec you can use any OpenAPI V3 validator, such as [swagger-cli](https://apitools.dev/swagger-cli/), [Spectral](https://stoplight.io/open-source/spectral/) or [speccy](http://speccy.io).

To lint and validate install your favorite tool and run:

<pre>
swagger-cli validate reference/anuto/openapi.yaml <i>(or)</i>
spectral lint reference/anuto/openapi.yaml <i>(or)</i>
speccy lint reference/anuto/openapi.yaml
</pre>

### Mock Server

To run a mock server based on the spec install [Prism](https://stoplight.io/prism), then:

<pre>
cd reference/anuto
prism mock openapi.yaml
</pre>

prism-cli 3.1.0 has a [bug](https://github.com/stoplightio/prism/pull/578) related to content negotiation and the `*/*` accept header. So you should explicitily send a `application/json` Accept header when using the mock server. So just using the browser won't usually work as expected (you will see a xml response instead of json).

Using [HTTPie](https://httpie.org):

<pre>
http http://127.0.0.1:4010/maps/original
http http://127.0.0.1:4010/maps/waiting_line?__example=waiting_line
http http://127.0.0.1:4010/maps/hurry?__example=hurry
http http://127.0.0.1:4010/tournaments
http http://127.0.0.1:4010/tournaments/123
http http://127.0.0.1:4010/tournaments/123/scores/1
http http://127.0.0.1:4010/tournaments/123/scores/my
</pre>


## Contributing

Thank you for your interest in Cartesi! Head over to our [Contributing Guidelines](CONTRIBUTING.md) for instructions on how to sign our Contributors Agreement and get started with Cartesi!

Please note we have a [Code of Conduct](CODE_OF_CONDUCT.md), please follow it in all your interactions with the project.

## License

This repository and all contributions are licensed under
[APACHE 2.0](https://www.apache.org/licenses/LICENSE-2.0). Please review our [LICENSE](LICENSE) file.

## Acknowledgments

- Original work