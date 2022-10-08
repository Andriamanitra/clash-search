# A website for searching puzzles on CodinGame

Background: the CG puzzle search site at http://eulerschezahl.herokuapp.com/codingame/puzzles/ (https://github.com/eulerscheZahl/CG-Tools) will discontinue working permanently on November 28th. The puzzle search is an important tool for players and contributors of [Clash of Code](https://www.codingame.com/multiplayer/clashofcode). It allows players to find the contribution page for the puzzles after a game – to fix bad test cases / validators, improve problem statements, or just leave feedback in the comment section. This project is an attempt to replace it with something that is hopefully faster and better at finding puzzles. To achieve this we use the excellent open source search engine [MeiliSearch](https://www.meilisearch.com/) to index and search documents. The front-end for the puzzle search is written using the [Svelte](https://svelte.dev/) framework.


## Instructions for scraping clashes from the undocumented CodinGame API

### Get all clashes

HTTP POST url: https://www.codingame.com/services/Contribution/getAcceptedContributions

Request body:

```json
["CLASHOFCODE"]
```
(change to "ALL" to get regular puzzles too)

To make this work you may need to copy headers from the request in Firefox dev tools on the [codingame site](https://www.codingame.com/contribute/community?mode=accepted&type=clashofcode). To craft the request with all the required headers I recommend using [Thunder client for VSCode](https://www.thunderclient.com/), but Postman or even just curl would also work.


### Get detailed information about a clash

HTTP POST url: https://www.codingame.com/services/Contribution/findContribution

Request body:

```json
["<publicHandle of the clash>", true]
```


### Using clashfetch.py to fetch all the clashes

1. Create & activate a virtual environment
2. Install requirements: `pip install httpx`
3. Modify the `clashfetch.py` script to say which handles you want to fetch
4. `python clashfetch.py`
5. Combine multiple .json files into one big array: `jq -n '[inputs]' clashes/*.json > clashes.json`


## Put clashes into MeiliSearch
1. Run MeiliSearch with `docker-compose up -d` (shut it down with `docker-compose down` when you're done)
2. `export MEILI_MASTER_KEY=MASTER_KEY`
3. `curl -X POST "http://localhost:7700/indexes/clashes/documents" -H "Content-Type: application/json" -H "Authorization: Bearer $MEILI_MASTER_KEY" --data-binary @clashes.json`
4. (optional) `curl -X PATCH "http://localhost:7700/indexes/clashes/settings" -H "Content-Type: application/json" -H "Authorization: Bearer $MEILI_MASTER_KEY" --data-binary @meili-indexes-clashes-settings.json`


## Developing front-end

* `cd frontend`
* Install dependencies: `npm install`
* Start developing with `npm run dev`
* Build with `npm run build`


## Running the whole thing
`docker-compose up -d` starts two services:
1. MeiliSearch on http://localhost:7700 
2. The front end (behind nginx) on http://localhost:8000 (this will serve the files from `frontend/dist` directory which is populated when you run `npm run build` – during development it's better to use `npm run dev` to see changes in real time)
