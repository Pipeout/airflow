run:
	sudo docker compose -f infra/compose.yaml up
build:
	sudo docker compose -f infra/compose.yaml up --build
down:
	sudo docker compose -f infra/compose.yaml down
