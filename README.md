docker run -v $(pwd):/app rasa/rasa:3.6.21-full init --no-prompt

docker run -v $(pwd):/app rasa/rasa:3.6.21-full train

docker run -v $(pwd):/app -p 5005:5005 rasa/rasa:3.6.21-full run


docker compose up
