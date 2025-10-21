Mocking API endpoints during local development provides many benefits for maintaining a productive and reliable development workflow.

We are introducing [WireMock](https://wiremock.org/) to mock API endpoints, allowing developers to work independently without reliance upon the existence, availability, performance, or current state of APIs provided by other apps.

Additionally, mocked endpoints enable frontend developers to implement features before the API has been updated to provide the necessary functionality.

## Setting up WireMock

WireMock operates through JSON mapping files stored in the `wiremock/mappings/` directory. Each JSON file defines an endpoint that responds to HTTP requests matching its specific `urlPattern` and returns a predefined responses object. For example, consider the following WireMock mapping file:

```json
{
  "request": {
    "method": "GET",
    "urlPattern": "/rosetta/data?.*iaid=C5067736.*"
  },
  "response": {
    "status": 200,
    "body": "{ \"digitised_discovery\": { \"id\": \"C5067736\", \"title\": \"Sample Document Title\", \"description\": \"This is a sample description of the document.\", \"date\": \"1945-05-08\", \"type\": \"Textual Record\" } }",
    "headers": {
      "Content-Type": "application/json"
    }
  }
}
```

The `urlPattern` field uses regular expressions to define flexible URL matching. The pattern `/rosetta/data?.*iaid=C5067736.*` will match any `GET` request to the `/rosetta/data` endpoint that includes the `iaid=C5067736` parameter, regardless of other query parameters or their order. This allows the mock to handle variations in the actual API calls while maintaining consistent test scenarios.

## Using the mocked endpoints

To use the mocked endpoints during local development, you'll need to update your `.env` file to use the Wiremock server URL, rather than the real API endpoint. For example, to use the Wiremock server for the delivery options API, you would set the following environment variable:

```
DELIVERY_OPTIONS_API_URL=http://mock-delivery-options-api:8080/rosetta/data
```

You will then need to rebuild your Docker containers to apply the changes:

```bash
docker-compose up --build
```
