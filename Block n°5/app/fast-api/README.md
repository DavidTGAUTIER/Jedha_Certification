For local use (on localhost:4000): 
docker build . -t fast_api_get_around
docker run -it -v "%cd%:/home/app" -p 4000:4000 -e PORT=4000 fast_api_get_around