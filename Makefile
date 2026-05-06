run:
	sudo docker compose -f infra/compose.yaml up --remove-orphans
build:
	sudo docker compose -f infra/compose.yaml up -d --build
down:
	sudo docker compose -f infra/compose.yaml down --remove-orphans
