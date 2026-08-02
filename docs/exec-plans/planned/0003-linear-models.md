# Planned Plan 0003: Certified Linear Models

Backlog: SQ-0037–SQ-0047.

## Goal

Compile selected R/Python/Julia linear-model specifications to one canonical matrix/contrast normal form; certify least-squares/rank computations; separately instantiate exact or asymptotic inferential theorems under explicit assumptions.

## Required work

- cross-language formula, categorical, missingness, weights, offset, and contrast semantics;
- canonical row IDs, response/design matrix, target contrast, covariance/df convention;
- OLS/WLS minimizer theorems including rank-deficient estimability;
- QR/LDL/Cholesky or residual-plus-conditioning witnesses;
- interval-certified coefficient/contrast results;
- exact Gaussian model theorem pack;
- sandwich/asymptotic claims that retain asymptotic labels;
- checked adapters for selected source package versions;
- cross-language exemplar and deliberate divergences.

Numerical optimality must never be reported as model adequacy, causal interpretation, or interval validity.
