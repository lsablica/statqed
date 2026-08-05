# Point-in-time dependency advisory queries

Status: **Experimental evidence**.

`query_osv.py` sends exact package/version pairs from the checked-in Python and
R prototype locks to the official OSV `querybatch` API. `--record` retains the
request, response, command interval, stdout, and stderr under
`../logs/security/run-20260805/`. `--verify` performs the same queries in a
temporary directory and checks only response structure and package alignment;
it does not overwrite the retained evidence.

These queries cover the prototype dependency graphs, not the language
toolchain binaries, operating-system packages, transitive native libraries, or
future StatQED production dependencies. A zero-result response is a
point-in-time observation, not a security guarantee. Network access to
`https://api.osv.dev/v1/querybatch` is required for a fresh query.
