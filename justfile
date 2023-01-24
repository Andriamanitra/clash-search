# environment variables are loaded from .env
set dotenv-load


mkdotenv:
    #!/usr/bin/env python3
    meili_master_key = input("Choose a master key for MeiliSearch: ")
    with open(".env", "w") as f:
        f.write(
            'PORT=8000'
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

meili-up:
    docker run -d --rm \
        --name clash-search-meili \
        --env MEILI_MASTER_KEY=$MEILI_MASTER_KEY \
        --env MEILI_ENV=$MEILI_ENV \
        -p 7700:7700 \
        -v $PWD/meili_data:/meili_data \
        getmeili/meilisearch:v0.29

meili-down:
    docker container stop clash-search-meili

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
            --output data/clashes/$clashid.json
    done

combine-clashes:
    jq -n '[inputs]' data/clashes/*.json > data/clashes.json

check-missing-clashes:
    #!/usr/bin/bash
    comm -23 <(jq -r '.[].publicHandle' data/list_of_clashes.json | sort) <(find data/clashes/ -name '*.json' -printf "%f\n" | awk -F. '$0=$1' | sort)

put-clashes fname="data/clashes.json": up
    curl -X POST "$VITE_MEILI_URL/indexes/clashes/documents" \
         -H "Content-Type: application/json" \
         -H "Authorization: Bearer $MEILI_UPDATE_KEY" \
         --data-binary @{{fname}}

configure-meili:
    curl -X PATCH "$VITE_MEILI_URL/indexes/clashes/settings" \
         -H "Content-Type: application/json" \
         -H "Authorization: Bearer $MEILI_MASTER_KEY" \
         --data-binary @meili_config/indexes-clashes-settings.json

make-keys:
    curl -X POST "$VITE_MEILI_URL/keys" \
         -H "Content-Type: application/json" \
         -H "Authorization: Bearer $MEILI_MASTER_KEY" \
         --data-binary @meili_config/make-public-key.json
    curl -X POST "$VITE_MEILI_URL/keys" \
         -H "Content-Type: application/json" \
         -H "Authorization: Bearer $MEILI_MASTER_KEY" \
         --data-binary @meili_config/make-update-key.json

check-new-clashes:
    python3 scripts/check_updates.py
