down:
	docker compose down

up:
	docker compose -f docker/docker-compose.prod.yml --env-file .env up -d
