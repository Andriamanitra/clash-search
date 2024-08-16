<script>
    export let clash;
    $: ({
        statement,
        testCases,
        inputDescription,
        outputDescription,
        constraints,
    } = clash?.lastVersion?.data);

    /**
     * Returns a new string with special formatting syntax removed
     * - bolded:    <<A>>
     * - variables: [[A]]
     * - constants: {{A}}
     * @param {string} txt
     */
    function removeFormatting(txt) {
        return txt
            .replaceAll(/<<(.+?)>>/g, "$1")
            .replaceAll(/\[\[(.+?)\]\]/g, "$1")
            .replaceAll(/\{\{(.+?)\}\}/g, "$1");
    }
</script>

<div class="card">
    <a
        class="card-header"
        href="https://codingame.com/contribute/view/{clash.publicHandle}"
    >
        <span class="title">{clash.title}</span>

        <span class="author"
            >by <a
                href="https://codingame.com/profile/{clash.codingamerHandle}"
            >
                {clash.nickname || "Anonymous"}
            </a>
        </span>
    </a>

    <div class="card-content">
        <p class="statement">{removeFormatting(statement)}</p>
        <div class="example test-in-out">
            <pre class="test-case in">{testCases[0].testIn}</pre>
            <pre class="test-case out">{testCases[0].testOut}</pre>
        </div>
        <details class="details">
            <summary>Details</summary>
            <h3 class="description-title">Input description</h3>
            <div class="description">{removeFormatting(inputDescription)}</div>
            <h3 class="description-title">Output description</h3>
            <div class="description">{removeFormatting(outputDescription)}</div>
            {#if constraints}
                <h3 class="description-title">Constraints</h3>
                <div class="description">{removeFormatting(constraints)}</div>
            {/if}
        </details>
        <details class="details test-cases">
            <summary>All test cases</summary>
            <div class="test-in-out">
                {#each testCases as testCase}
                    <pre class="test-case in">{testCase.testIn}</pre>
                    <pre class="test-case out">{testCase.testOut}</pre>
                {/each}
            </div>
        </details>
    </div>
</div>

<style>
    .card-content {
        display: flex;
        flex-direction: column;
        gap: 15px;
    }
    .statement, .description {
        white-space: pre-wrap;
    }
    .statement {
        max-height: 10em;
        overflow: auto;
    }
    h3 {
        margin: 5px 0;
    }
    h3:nth-of-type(n+2) {
        margin-top: 1em;
    }
    .test-case::before {
        content: "";
        position: absolute;
        font-size: 0.8em;
        margin-top: -2em;
        color: var(--gray);
    }
    .in::before {
        content: "Input";
    }
    .out::before {
        content: "Output";
    }
    .details summary {
        cursor: pointer;
    }
    .details {
        outline: 1px solid var(--gray);
        padding: 0.5em;
    }
    .details :nth-child(2) {
        margin-top: 12px;
    }
    .test-in-out {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2ch;
    }
    .test-case {
        flex-grow: 1;
        margin: 1em 0 0 0;
        padding: 3px 1ch;
        outline: 1px solid var(--gray);
        max-height: 30em;
        overflow: auto;
    }
</style>
