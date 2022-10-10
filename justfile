# environment variables are loaded from .env
set dotenv-load


mkdotenv:
    #!/usr/bin/env python3
    meili_master_key = input("Choose a master key for MeiliSearch: ")
    with open(".env", "w") as f:
        f.write(
            f'MEILI_ENV=development\n'
            f'MEILI_MASTER_KEY="{meili_master_key}"\n'
            f'MEILI_UPDATE_KEY="{meili_master_key}"\n'
            'LAST_UPDATED_TIME=\n'
            'CODINGAME_COOKIES=\n'
            'VITE_MEILI_URL="http://localhost:7700"\n'
            f'VITE_MEILI_SEARCH_KEY="{meili_master_key}"\n'
        )
    print("Wrote .env (WARNING: this configuration is for DEVELOPMENT ONLY)")

install-deps:
    cd frontend && npm install

dev:
    cd frontend && npm run dev

build:
    cd frontend && npm run build

up:
    docker-compose up -d

down:
    docker-compose down

get-clashes +CLASHIDS:
    #!/usr/bin/bash
    for clashid in {{CLASHIDS}}; do
        curl -Ss -X POST "https://www.codingame.com/services/Contribution/findContribution" \
            -H "Content-Type: application/json" \
            --data "[\"$clashid\", true]" \
            --output tclashes/$clashid.json
    done

combine-clashes:
    jq -n '[inputs]' data/clashes/*.json > data/clashes.json

put-clashes fname="data/clashes.json": up
    curl -X POST "$VITE_MEILI_URL/indexes/clashes/documents" \
         -H "Content-Type: application/json" \
         -H "Authorization: Bearer $MEILI_UPDATE_KEY" \
         --data-binary @{{fname}}

configure-meili:
    curl -X PATCH "$VITE_MEILI_URL/indexes/clashes/settings" \
         -H "Content-Type: application/json" \
         -H "Authorization: Bearer $MEILI_MASTER_KEY" \
         --data-binary @meili-indexes-clashes-settings.json

check-new-clashes: up
    python3 scripts/check_new_clashes.py

@show-links:
    echo "Meili: http://localhost:7700"
    echo "Front: http://localhost:8000"
