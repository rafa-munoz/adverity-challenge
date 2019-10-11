Getting started
---------------

In order to run the services, you must have
[Docker](https://www.docker.com/) installed.

Running the develop environment
_______________________________

Build all services' images:

```bash
docker-compose build
```

Start all services:

```bash
docker-compose up
```

Now you can open http://localhost:8000

Running the tests (fast check)
______________________________

```bash
docker-compose run --rm --entrypoint 'bash scripts/run-tests.sh' web
```

Running the tests (development style)
_____________________________________

Enter into the web container:

```bash
docker-compose run --rm --entrypoint 'bash' web
```

Run the tests:

```bash
source scripts/run-tests.sh
```

Improvements
------------

* UI: make it more beautiful.
* UI: instead of resetting every time the forms, show what was selected
  last time.
* Use [Django cache](https://docs.djangoproject.com/en/2.2/topics/cache/) to
  speed up calls to `app.extraction.get_data()`. Depending on the update
  frequency of that endpoint, we would tune the timeout cache.
* Use Django forms with `MultipleChoiceField` instead of writing it manually.
* Create tests for the views.
* Use Python Alpine image.
