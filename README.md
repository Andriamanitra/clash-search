# A website for searching puzzles on CodinGame

Background: the CG puzzle search site at http://eulerschezahl.herokuapp.com/codingame/puzzles/ (https://github.com/eulerscheZahl/CG-Tools) will discontinue working permanently on November 28th. The puzzle search is an important tool for players and contributors of [Clash of Code](https://www.codingame.com/multiplayer/clashofcode). It allows players to find the contribution page for the puzzles after a game – to fix bad test cases / validators, improve problem statements, or just leave feedback in the comment section. This project is an attempt to replace it with something that is hopefully faster and better at finding puzzles. To achieve this we use the excellent open source search engine [MeiliSearch](https://www.meilisearch.com/) to index and search documents. The front-end for the puzzle search is written using the [Svelte](https://svelte.dev/) framework.


## Quickstart using justfile

*If you don't want to install `just`, you can also look at the `justfile` and run the equivalent commands manually*

Before getting started make sure you have the following installed:
* [Just](https://github.com/casey/just) (command runner, bit like `make` but more advanced)
* [Docker](https://www.docker.com/) (containerization)
* [Docker-compose](https://github.com/docker/compose/releases) (container orchestration)
* [curl](https://curl.se/) (for making http requests)
* [jq](https://github.com/stedolan/jq) (for processing JSON files)
* [node.js](https://nodejs.org/en/) (for developing front-end)
* [Python3](https://www.python.org/) (for helper scripts)

1. `just mkdotenv` – creates `.env` file with default configuration for development
1. `just install-deps build` – installs npm dependencies and builds the frontend
1. `just meili-up` – uses Docker to start MeiliSearch (on http://localhost:7700)
1.  Acquire some clashes for test data:
```just get-clashes 52980368bdbd05abdd789a04173b57b0fdea 682102420fbce0fce95e0ee56095ea2b9924```
1. `just combine-clashes` – Combine the clashes into a single JSON file (stored in `data/clashes.json`)
1. `just put-clashes data/clashes.json`

When you're done use `just meili-down` to shut down the Meili docker container. The data for MeiliSearch will be preserved under `meili_data/` for the next time.

To acquire all of the clashes you can follow the instructions in the dedicated section for using the undocumented CodinGame API (`scripts/clashfetch.py` may also help in the process).


## Frontend development
* `cd frontend`
* Install dependencies: `npm install`
* Start developing with `npm run dev`
* Build with `npm run build`


## Instructions for scraping clashes from the undocumented CodinGame API

### Get a list of all clashes

HTTP POST url: https://www.codingame.com/services/Contribution/getAcceptedContributions

Request body:

```json
["CLASHOFCODE"]
```
(change to "ALL" to get regular puzzles too)

To make this work you may need to copy headers (cookies) from the request in Firefox dev tools on the [codingame site](https://www.codingame.com/contribute/community?mode=accepted&type=clashofcode). To craft the request with all the required headers I recommend using [Thunder client for VSCode](https://www.thunderclient.com/), but Postman or even just curl would also work.

### Get detailed information about a clash

HTTP POST url: https://www.codingame.com/services/Contribution/findContribution

Request body:

```json
["<publicHandle of the clash>", true]
```

This end point does not seem to require headers (cookies), but if you do provide them you may get extra information that is only accessible to users above a certain level (for example the solution to the problem).
