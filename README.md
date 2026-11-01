# contoso-payments

> **Contoso Bank is fictional.** This is not a real bank, and this is not
> production payments code. It is a small demo service for
> [APMX](https://github.com/danielmeppiel/apmx): it shows a repository that
> takes changes from a versioned **agentic factory** and accepts its pull
> requests **by proof**.

## What is here

| Path | What |
| --- | --- |
| `src/payments/` | A small outgoing-payments service: [wires](src/payments/wires.py) (`submit_wire`), the [payee registry](src/payments/payees.py), the [approval queue](src/payments/approvals.py), the [ledger](src/payments/ledger.py) and integer-cent [money](src/payments/money.py) helpers. Standard library only. |
| `tests/` | The existing `unittest` suite. |
| `docs/` | [How wires work](docs/wires.md). |
| `request.md` | The intent the factory implements: [hold wires of $10,000 or more to a new payee for a second approval](request.md). |
| `acceptance/` | **The bank's own definition of done**: [`wire-hold.feature`](acceptance/wire-hold.feature) and its step definitions. The factory's checks read them from this repository's original bytes and reject any change that touches them. |
| `apm-policy.yml` | Which factory this repository accepts (by definition digest) and which workflow may sign its deliveries. |
| `.github/workflows/factory.yml` | Runs the factory in CI through apmx's reusable `run.yml`. |
| `.github/workflows/audit.yml` | The gate: `apmx audit` on every pull request. |

## Run it locally

```sh
PYTHONPATH=src python3 -m unittest discover -s tests          # existing tests
python3 -m pip install --require-hashes -r <factory>/checks/requirements.txt   # Behave 1.3.3
PYTHONPATH=src behave acceptance                              # acceptance: 2 scenarios fail until the change lands
```

## How a change arrives

1. **The factory is reviewed once.**
   [apmx-demo-factory](https://github.com/danielmeppiel/apmx-demo-factory) `v2.0.0`
   is a generic feature factory: five agent contracts (plan, specify, build,
   document, review) and the checks that judge them. Its contracts say
   "implement the intent in `request.md` so the repository's acceptance
   scenarios pass". Its *definition digest* fingerprints those contracts,
   checks and pinned capabilities at a commit.
2. **It runs in CI and signs what it delivers.**
   [`factory.yml`](.github/workflows/factory.yml) calls apmx's reusable
   `run.yml`: the agent runs in one job, a fresh job with no agent reruns the
   checks and writes the receipt, a third job signs a verification summary over
   the delivered files with GitHub's OIDC identity, and the deliver job commits
   **only the delivered files**. The pull request carries code, never a receipt.
3. **This repository accepts the PR by proof.**
   [`audit.yml`](.github/workflows/audit.yml) runs `apmx audit`, the required
   check on `main`, on `pull_request_target` (main's copy of the gate runs; a PR
   cannot edit it, and nothing from the PR is executed). It passes only if every
   changed file is covered by one signed verification summary from the pinned
   workflow, the factory digest is on [`apm-policy.yml`](apm-policy.yml)'s allow
   list, its checks passed, its dependencies audit clean, and the PR is built on
   the base the factory read. Anything else is exit 1. Human pull requests fail
   it as "not a factory delivery" and are merged through the normal path.

## Run the factory in CI

- **Live** needs a model credential: a fine-grained personal access token with
  the **Copilot Requests** account permission and no repository access, stored
  as `COPILOT_GITHUB_TOKEN`
  (`gh secret set COPILOT_GITHUB_TOKEN --repo danielmeppiel/contoso-payments`).
- **Hermetic rehearsal** needs no secret: apmx's protocol fixture stands in for
  the agent. It is a plumbing test only; its digest is not on the allow list,
  so `audit` rejects its pull request.

```sh
gh workflow run factory.yml --repo danielmeppiel/contoso-payments -f mode=live
```

With a `DELIVERY_PR_TOKEN` secret (Contents and Pull requests write, this
repository only) run.yml opens the pull request itself. Without it, run.yml
builds the delivered commit and the `publish` job pushes the branch and prints
the `gh pr create` command (pull requests opened with the job's own
`GITHUB_TOKEN` never start `audit.yml`).

## Limits

- The signature authenticates *which workflow* vouched for a receipt, not that
  the agent is trustworthy. Checks assess their stated scope.
- Agents run natively on the runner: this is not a sandbox.
- A local run on a laptop is unsigned: it proves content binding, not who ran
  it, so this repository's policy (`require_signed: true`) does not accept it.
