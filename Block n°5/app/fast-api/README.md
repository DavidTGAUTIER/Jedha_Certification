For local use (on localhost:4000): 
docker build . -t getaround
windows : docker run -it -v "%cd%:/home/app" -p 4000:4000 -e PORT=4000 getaround
linux   : docker run -it -v "$(pwd):/home/app" -p 4000:4000 -e PORT=4000 getaround

For web:
https://get-around-fastapi.herokuapp.com/ # add /docs to see documentation

step for heroku (to create web app in your own):
* [install heroku](https://devcenter.heroku.com/articles/heroku-cli)
* heroku container:login (or heroku login if you not already login) 
* heroku create get-around-fastapi --region eu (create image on eu heroku server)
* heroku container:push web -a get-around-fastapi (push the image on registry.heroku)
* heroku container:release web -a get-around-fastapi(equivalent to `docker run` with heroku)
* heroku open -a get-around-fastapi (launch app on heroku server and open port to connect to web)
* heroku logs --tail -a get-around-fastapi(debugging and display logs)

