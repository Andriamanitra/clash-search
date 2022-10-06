<script>
    import { MeiliSearch } from "meilisearch";
    const client = new MeiliSearch({
        host: "http://localhost:7700",
        apiKey: "MASTER_KEY",
    });
    const LIMIT = 10;
    const clashIndex = client.index("clashes");
    let offset = 0;
    let query = "";
    let results = { hits: [] };
    function handleSearchChange(ev) {
        offset = 0;
        searchClashes();
        ev.preventDefault();
    }
    function searchClashes() {
        if (query.length < 2) {
            results = { hits: [] };
        } else {
            clashIndex
                .search(query, { limit: LIMIT, offset: offset })
                .then((r) => {
                    results = r;
                });
        }
    }
    function previousPage() {
        offset = Math.max(0, offset - LIMIT);
        searchClashes();
    }
    function nextPage() {
        offset = offset + LIMIT;
        searchClashes();
    }
    $: clashes = [...results["hits"]];
    $: console.log(results);
</script>

<header>
    <h1>Clash search</h1>
    <form on:submit={handleSearchChange}>
        <input
            id="searchbox"
            name="searchbox"
            type="text"
            bind:value={query}
            placeholder="search by title, statement, tests..."
            minlength="3"
            autofocus
        />
    </form>
</header>
<main>
    {#if results.estimatedTotalHits}
        <p>
            Results {offset + 1} - {offset + clashes.length} (of approximately {results.estimatedTotalHits}
            results in total)
        </p>
        <button on:click={previousPage} disabled={offset == 0}>
            Previous page
        </button>
        <button on:click={nextPage} disabled={clashes.length < LIMIT}>
            Next page
        </button>
    {:else}
        <p>No results</p>
    {/if}
    {#each clashes as { title, nickname, publicHandle, codingamerHandle, lastVersion }}
        <div>
            <h2>
                <a href="https://codingame.com/contribute/view/{publicHandle}">
                    {title}
                </a>
                (by
                <a href="https://codingame.com/profile/{codingamerHandle}"
                    >{nickname || "Anonymous"}</a
                >)
            </h2>
            <div class="clash-statement">{lastVersion.data.statement}</div>
        </div>
    {/each}
</main>

<style>
    input:invalid {
        color: red;
    }
    h2 {
        margin: 1ch 0 0 0;
    }
    .clash-statement {
        max-height: 4rem;
        max-width: 80ch;
        overflow-y: auto;
    }
</style>
