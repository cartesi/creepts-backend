# REST API

The REST API is defined in OpenAPI V3, in the directory `reference/anuto/`.
That also includes examples of each endpoint response.

## Documentation

### Using docker

    docker run --rm -v $(pwd)/reference/anuto:/project -p 5000:5000 wework/speccy serve openapi.yaml

### Running locally

Install [speccy](http://speccy.io), then run:

    speccy serve reference/anuto/openapi.yaml

Open documentation at [http://localhost:5000/](http://localhost:5000/)

## Validation

To validate the spec you can use any OpenAPI V3 validator, such as [swagger-cli](https://apitools.dev/swagger-cli/), [Spectral](https://stoplight.io/open-source/spectral/) or [speccy](http://speccy.io).

To lint and validate install your favorite tool and run:

<pre>
swagger-cli validate reference/anuto/openapi.yaml <i>(or)</i>
spectral lint reference/anuto/openapi.yaml <i>(or)</i>
speccy lint reference/anuto/openapi.yaml
</pre>

## Mock Server

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
