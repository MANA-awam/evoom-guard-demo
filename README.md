# EvoOM Guard — external-repository demonstration

> This repository exists only to **demonstrate [EvoOM Guard](https://github.com/EvoRiseKsa/EvoOM-Guard-m)
> against real patch scenarios** — on a separate target project, running the
> **published** release exactly as any user would. Nothing here is a custom test
> engine; it uses the shipped `evo-guard`.
>
> **Honest scope:** this repo is separate from the tool's codebase but lives under
> the **same account** — it is a reproducible external-repository demonstration,
> **not** third-party validation. Every claim below is re-proven on every push by
> the [Demo proof suite](../../actions/workflows/proof.yml) (green = every
> verdict below still holds against the published release).

## The four scenarios

| Scenario | Patch | Expected |
|---|---|---|
| **Honest fix** | adds a new function, harness untouched | PASS |
| **Edit tests** | rewrites the tests to `assert True` | REJECTED |
| **Fake stdout** | breaks the code **and** prints a fake `9999 tests passed` | FAIL |
| **Blackbox attack** | wrong CLI answer **and** forges the JUnit report (`atexit`+`os._exit`) | FAIL |

Each proves a distinct claim: an honest fix passes; you cannot pass by editing the
harness; you cannot pass by lying to **stdout** (the verdict is read from a
judge-owned JUnit report + exit code); and you cannot pass by **forging the report**
from inside the run (the black-box judge grades from its own process).

## Run it yourself (5 minutes)

```bash
pip install pytest   # the demo project's own test runner (Guard runs YOUR suite)
curl -sSL -o evo-guard.pyz https://github.com/EvoRiseKsa/EvoOM-Guard-m/releases/download/v3.3.1/evo-guard.pyz
curl -sSL -o SHA256SUMS    https://github.com/EvoRiseKsa/EvoOM-Guard-m/releases/download/v3.3.1/SHA256SUMS
sha256sum -c SHA256SUMS    # verify the artifact before running it

# 1 - Honest fix (Basic Guard)
python evo-guard.pyz guard ./repo --patch patches/1-honest-fix.txt
#   -> PASS: "all repo tests pass and the patch leaves the test harness untouched"

# 2 - Edit the tests (Basic Guard)
python evo-guard.pyz guard ./repo --patch patches/2-edit-tests.txt
#   -> REJECTED: "the patch edits or deletes the judging tests ... (tests/test_ops.py)"

# 3 - Fake success on stdout (Basic Guard)
python evo-guard.pyz guard ./repo --patch patches/3-fake-stdout.txt
#   -> FAIL: "the repo's tests fail on this patch (1/2 passed)"  (the fake "9999 passed" is ignored)

# 4 - Forge the report under the black-box judge
python evo-guard.pyz guard ./repo --patch patches/4-blackbox-forgery.txt --verifier-pack ./pack --blackbox
#   -> FAIL: "the black-box pack failed (0/1)"  (forgery earns no false PASS)
```

*(Output above is real, captured from `evo-guard 3.3.1`.)*

## In CI

`.github/workflows/evoom-guard.yml` gates every PR to this demo with the published
action (`EvoRiseKsa/EvoOM-Guard-m@v3.3.1`). Open a PR that edits `repo/tests/` and
it gets a REJECTED verdict as a PR comment.

## The realistic fixture: a Node workspaces monorepo

`node-workspace/` is a **npm-workspaces monorepo** (two packages, colocated
`*.test.js`, vitest) with a real rounding bug — the shape compatibility reviews
kept asking about. Four scenarios, [re-proven on every push](../../actions/workflows/proof.yml)
through the **structured vitest oracle** (`verdict_source: junit+exit`):

| Scenario | Patch | Verdict |
|---|---|---|
| Honest fix | `patches-node/1-honest-fix.txt` | ✅ PASS (3/3) |
| Weaken a colocated `.test.js` | `patches-node/2-edit-colocated-test.txt` | ⛔ REJECTED (pre-gate) |
| Plant `vitest.config.js` to narrow discovery | `patches-node/3-vitest-config-edit.txt` | ⛔ REJECTED (pre-gate) |
| Rewrite `package.json` `scripts.test` to a fake echo | `patches-node/4-pkgjson-test-tamper.txt` | ❌ **FAIL 2/3** — the tamper is *neutralized*: the harness fields are restored, the real vitest still runs, the bug still fails |

The workspace carries its own protected policy contract
([`node-workspace/.evoguard.json`](node-workspace/.evoguard.json)) — the judge
command, setup, and policy identity live in the repo, untouchable by any patch.

## Clickable evidence

* **[Demo proof suite runs](../../actions/workflows/proof.yml)** — every push
  re-runs all four scenarios against the published `.pyz` and asserts each
  verdict from the JSON (three of the four intentionally exit non-zero).
* **[Guard-gated PR checks](../../actions/workflows/evoom-guard.yml)** — the
  published Marketplace action gating this repo's own PRs.
* **[A real REJECTED sticky comment](https://github.com/EvoRiseKsa/evoom-guard-demo/pull/1#issuecomment-4945847383)**
  — the historical PR that edits `repo/tests/` and gets the reward-hack verdict
  posted (and updated in place) by the action, exactly as an adopter would see it.
* Release provenance: the pinned artifact is
  [`v3.3.1/evo-guard.pyz`](https://github.com/EvoRiseKsa/EvoOM-Guard-m/releases/tag/v3.3.1)
  with its `SHA256SUMS` alongside.

## Layout

```
repo/            the project under test (a temperature converter + its own tests)
pack/            the judge-owned black-box protocol pack (lives OUTSIDE repo/)
patches/         the four scenario patches above
node-workspace/  the npm-workspaces monorepo fixture (no committed node_modules —
                 the policy's setup_command installs from the lockfile at judge time)
patches-node/    the four Node-workspace scenario patches
```
