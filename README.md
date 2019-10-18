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

About data refresh
__________________

With the current implementation, we do not know for sure how often the source
file is getting updated. It could even happen that after 24 hours + 1 second,
the source file gets updated. However, if we retrieved the file one second
before, we would have the same data for 2 days.

Looking to the headers, we know when it was last modified and the ETag:

```
* Connected to adverity-challenge.s3-website-eu-west-1.amazonaws.com (52.218.100.60) port 80 (#0)
> GET /DAMKBAoDBwoDBAkOBAYFCw.csv HTTP/1.1
> Host: adverity-challenge.s3-website-eu-west-1.amazonaws.com
> User-Agent: curl/7.64.0
> Accept: */*
>
< HTTP/1.1 200 OK
< x-amz-id-2: zIxAhbME9HVG3yGxRH/KwKa50VF5GAZ7Yip7i1NmnZsw1clbATUeHhQxiARSc3D26hnTgYVaANA=
< x-amz-request-id: 944CF0D3F7E57FD8
< Date: Fri, 18 Oct 2019 08:25:33 GMT
< Last-Modified: Fri, 06 Sep 2019 12:32:23 GMT
< ETag: "4e48680b2bbfeacf13bdf7e5abdef8e0"
< Content-Type: text/csv
< Content-Length: 2169192
< Server: AmazonS3
```

We can use this data to improve the application:

* Create a table with two fields: `last_modified` (index) and `etag`.
* Program a worker every 24 hours. This worker would check reading the headers
  if the source has been updated. In case it did not, retry again in one minute.
* Once the source has been updated and the new data was stored, update the
  table with the new `last_modified` and `etag` values.


Other improvements
__________________

* UI: make it more beautiful.
* UI: instead of resetting every time the forms, show what was selected
  last time.
* Use [Django cache](https://docs.djangoproject.com/en/2.2/topics/cache/) to
  speed up calls to `app.extraction.get_data()`. Depending on the update
  frequency of that endpoint, we would tune the timeout cache.
* Use Django forms with `MultipleChoiceField` instead of writing it manually.
* Create tests for the views.
* Use Python Alpine image.
