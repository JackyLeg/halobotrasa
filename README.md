docker run -v $(pwd):/app rasa/rasa:3.6.21-full init --no-prompt
<!-- to train -->
docker run -v $(pwd):/app rasa/rasa:3.6.21-full train --domain domain/

<!-- to run with docker -->
docker run -v $(pwd):/app -p 5005:5005 rasa/rasa:3.6.21-full run

<!-- to run rasa shell with docker -->
docker run -it -v $(pwd):/app rasa/rasa:3.6.21-full shell

docker compose up


# Training — specify domain dir
rasa train --domain domain/ --data data/

# Running — just point to the model, no --domain needed
rasa run --enable-api --cors "*"