pip install copier

copier copy https://github.com/DelliBenedettiDanilo/template_arch_django.git .\ --trust
#Con .\ gli dico che deve copiare il template nella cartella corrente


# build + avvio
docker compose -f docker-compose.dev.yml up -d --build

# log del project in tempo reale
docker compose -f docker-compose.dev.yml logs -f web

# stop
docker compose -f docker-compose.dev.yml down

# stop con eliminazione dei dati (volumi)
docker compose -f docker-compose.dev.yml down -v
