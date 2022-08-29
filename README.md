# Vend-O-Matic
You may run this project with by building the docker image in the project directory with the provided Dockerfile, and running the image.
```
docker build --tag foo .
docker run -p 8000:8000 foo
```
The name, "foo" may be replaced with whichever name the user finds desirable. Once the docker image is running, from a separate command line, it may be queried with
```
curl -v -X $request-type 127.0.0.1:8000/$url
```
where *$request-type* is the html request type ("GET", "PUT", "DELETE"), and $url is the desired url ("/", "/inventory", etc).

This project may also be run outside of docker with
```
python -m flask --app=vendomatic.py run -p 8000
```
and queried similarly.
