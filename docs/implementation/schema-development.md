# Schema Development Guide

For each schema change:

1. update controlled semantic prose;
2. update CDDL and optional JSON projection;
3. add valid/minimal/maximal examples;
4. add malformed, unknown-extension, duplicate-key, numeric-boundary, and resource fixtures;
5. produce reviewed canonical bytes and digests;
6. compare at least two implementations;
7. assess migrations and theorem/artifact effects;
8. regenerate bindings through the documented generator.

Never edit generated bindings by hand.
