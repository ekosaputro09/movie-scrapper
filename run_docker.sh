docker kill movie-scrapper && docker rm movie-scrapper
docker build -t movie-scrapper . && docker run --name movie-scrapper -it -d --restart unless-stopped movie-scrapper