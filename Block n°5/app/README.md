For local use (on localhost:4000):</br>
docker build . -t getaround-app</br>
windows : docker run -it -v "%cd%:/home/app" -p 4000:4000 -e PORT=4000 getaround-app</br>
linux   : docker run -it -v "$(pwd):/home/app" -p 4000:4000 -e PORT=4000 getaround-app