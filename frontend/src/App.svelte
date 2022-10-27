<script>
  import { MeiliSearch } from "meilisearch";
  import GithubLink from "./lib/GithubLink.svelte";

  const client = new MeiliSearch({
    host: import.meta.env.VITE_MEILI_URL,
    apiKey: import.meta.env.VITE_MEILI_SEARCH_KEY,
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

  let dark = true;

  $: clashes = [...results["hits"]];
</script>

<header>
  <h1>Clash search</h1>
  <div class="header-links">
    <GithubLink repo="andriamanitra/clash-search" />
    <button
      class="darkmode-switch"
      title="Toggle dark mode"
      on:click={() => {
        document.getElementsByTagName("body")[0].toggleAttribute("dark");
        dark = !dark;
      }}
    >
      {dark ? "☀️" : "🌙"}
    </button>
  </div>
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
    <p class="info">
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
          class="card-header"
          href="https://codingame.com/contribute/view/{publicHandle}"
        >
          <span class="title">{title}</span>

          <span class="author"
            >by <a href="https://codingame.com/{codingamerHandle}">
              {nickname || "Anonymous"}
            </a>
          </span>
        </a>

        <p class="card-content">
          {lastVersion.data.statement}
        </p>
      </div>
    {/each}
  </div>
</main>
