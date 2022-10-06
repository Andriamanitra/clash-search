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
      clashIndex.search(query, { limit: LIMIT, offset: offset }).then((r) => {
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
    <div class="container">
      <p>No results</p>
    </div>
  {/if}
  <div class="container">
    {#each clashes as { title, nickname, publicHandle, codingamerHandle, lastVersion }}
      <div class="card">
        <a
          class="card-body"
          href="https://codingame.com/contribute/view/{publicHandle}"
        >
          <span class="title">{title}</span>
          <span class="clash-statement">
            {lastVersion.data.statement}
          </span>
        </a>
        <a class="user" href="https://codingame.com/profile/{codingamerHandle}">
          <span class="user-info">by {nickname || "Anonymous"}</span>
        </a>
      </div>
    {/each}
  </div>
</main>
