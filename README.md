docker run --rm -v $(pwd):/app rasa/rasa:3.6.21-full init --no-prompt
<!-- to validate -->
docker run --rm -v $(pwd):/app rasa/rasa:3.6.21-full data validate --domain domain --data data/
<!-- to train -->
docker run --rm -v $(pwd):/app rasa/rasa:3.6.21-full train --domain domain --data data/
<!-- to run with docker -->
docker run --rm -v $(pwd):/app -p 5005:5005 rasa/rasa:3.6.21-full run

<!-- to run rasa shell with docker -->
docker run -it -v $(pwd):/app rasa/rasa:3.6.21-full shell

docker compose up


# Training — specify domain dir
rasa train --domain domain/ --data data/

# Running — just point to the model, no --domain needed
rasa run --enable-api --cors "*"



cloudflared tunnel --url http://localhost:5005   

https://jackyleg.github.io