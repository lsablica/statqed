#!/usr/bin/env bash
set -u

prototype_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
package_dir="$prototype_dir/package"
development_source_lock="$prototype_dir/development-cran-source-lock.tsv"
repository_root=$(CDPATH= cd -- "$prototype_dir/../../../.." && pwd)
state_root=${STATQED_R_STATE_ROOT:-/tmp/statqed-sq0002-r}
development_source_cache=${STATQED_R_DEV_SOURCE_CACHE:-$state_root/dev-cran-sources}
floor_prefix=${STATQED_R_FLOOR_PREFIX:-$state_root/envs/r-4.4.3}
run_tag=${STATQED_R_RUN_TAG:-20260803}
log_dir=${STATQED_R_LOG_DIR:-$repository_root/docs/research/toolchain-prototypes/logs/r/run-$run_tag}
run_instance=${STATQED_R_RUN_INSTANCE:-$(date --utc +%Y%m%dT%H%M%S)-$RANDOM}
run_root="$state_root/runs/run-$run_tag-$run_instance"

# Keep conda's writable state in the disposable probe root. These variables
# are also recorded in the evidence fragment so an offline lock recreation
# does not depend on the invoking user's global conda configuration.
export XDG_CACHE_HOME=${XDG_CACHE_HOME:-$state_root/cache}
export CONDA_PKGS_DIRS=${CONDA_PKGS_DIRS:-$state_root/pkgs}
export CONDA_ENVS_PATH=${CONDA_ENVS_PATH:-$state_root/envs}

mkdir -p "$log_dir" "$run_root"

run_logged() {
  local label=$1
  local working_directory=$2
  shift 2
  local start
  local end
  local status
  start=$(date --utc +%Y-%m-%dT%H:%M:%SZ)
  (
    cd "$working_directory" || exit 125
    "$@"
  ) >"$log_dir/$label.stdout" 2>"$log_dir/$label.stderr"
  status=$?
  end=$(date --utc +%Y-%m-%dT%H:%M:%SZ)
  {
    printf 'start=%s\n' "$start"
    printf 'end=%s\n' "$end"
    printf 'cwd=%s\n' "$working_directory"
    printf 'exit_status=%s\n' "$status"
    printf 'argv='
    printf '%q ' "$@"
    printf '\n'
  } >"$log_dir/$label.command"
  return "$status"
}

capture_host() {
  run_logged host-uname "$repository_root" uname -a
  run_logged host-os-release "$repository_root" /usr/bin/env -i PATH=/usr/bin:/bin /usr/bin/cat /etc/os-release
  run_logged host-locale "$repository_root" locale
}

prepare_dev_library() {
  local dev_library=$1
  local archive
  local expected_sha256
  local install_order
  local package
  local source_url
  local version
  local actual_package
  local actual_version
  mkdir -p "$dev_library" "$development_source_cache"
  while IFS=$'\t' read -r install_order package version source_url expected_sha256; do
    [ "$install_order" = install_order ] && continue
    archive="$development_source_cache/${package}_${version}.tar.gz"
    if [ ! -f "$archive" ]; then
      printf 'fetch\t%s\t%s\n' "$package" "$source_url"
      curl --fail --location --proto '=https' --tlsv1.2 --silent --show-error \
        --output "$archive" "$source_url" || return 1
    else
      printf 'reuse-verified-cache\t%s\t%s\n' "$package" "$archive"
    fi
    printf '%s  %s\n' "$expected_sha256" "$archive" | sha256sum --check --status || {
      printf 'SHA-256 mismatch for %s\n' "$archive" >&2
      return 1
    }
    actual_package=$(tar -xOzf "$archive" "$package/DESCRIPTION" | sed -n 's/^Package:[[:space:]]*//p') || return 1
    actual_version=$(tar -xOzf "$archive" "$package/DESCRIPTION" | sed -n 's/^Version:[[:space:]]*//p') || return 1
    [ "$actual_package" = "$package" ] && [ "$actual_version" = "$version" ] || {
      printf 'Locked metadata mismatch for %s: got %s %s\n' "$archive" "$actual_package" "$actual_version" >&2
      return 1
    }
    printf 'install\t%s\t%s\t%s\n' "$install_order" "$package" "$version"
    R CMD INSTALL --library="$dev_library" "$archive" || return 1
  done <"$development_source_lock"
  Rscript --vanilla -e 'lock <- read.delim(commandArgs(TRUE)[1], check.names = FALSE, stringsAsFactors = FALSE); db <- installed.packages(); closure <- unique(c("testthat", unlist(tools::package_dependencies("testthat", db = db, recursive = TRUE, which = c("Depends", "Imports", "LinkingTo"))))); base <- rownames(installed.packages(priority = c("base", "recommended"))); closure <- sort(setdiff(closure, base)); expected <- sort(lock$package); stopifnot(identical(closure, expected)); cat("locked recursive source closure verified:", length(expected), "packages\n")' "$development_source_lock" || return 1
}

runtime_probe() {
  local label=$1
  local r_binary=$2
  local rscript_binary=$3
  local library_mode=$4
  local work_dir="$run_root/$label"
  local build_dir="$work_dir/build"
  local check_dir="$work_dir/check"
  local install_library="$work_dir/install-library"
  local runtime_library
  local tarball
  mkdir -p "$build_dir" "$check_dir" "$install_library"

  if [ "$library_mode" = dev ]; then
    runtime_library="$work_dir/test-library"
    export R_LIBS_USER="$runtime_library"
    export R_LIBS_SITE="$work_dir/empty-site-library"
    mkdir -p "$R_LIBS_SITE"
    export R_ENVIRON_USER=/dev/null
    export R_PROFILE_USER=/dev/null
    export TZ=UTC
    export LC_ALL=C.UTF-8
    run_logged "$label-development-source-lock-digest" "$repository_root" sha256sum "$development_source_lock" || return 1
    run_logged "$label-dependency-source-install" "$repository_root" prepare_dev_library "$runtime_library" || return 1
  else
    runtime_library="$floor_prefix/lib/R/library"
    export R_LIBS_USER="$work_dir/empty-user-library"
    mkdir -p "$R_LIBS_USER"
  fi
  export R_ENVIRON_USER=/dev/null
  export R_PROFILE_USER=/dev/null
  export TZ=UTC
  export LC_ALL=C.UTF-8

  run_logged "$label-r-version" "$repository_root" "$r_binary" --version || return 1
  run_logged "$label-r-config" "$repository_root" "$r_binary" CMD config --all || return 1
  run_logged "$label-package-lock" "$repository_root" "$rscript_binary" --vanilla -e 'wanted <- unique(c("testthat", unlist(tools::package_dependencies("testthat", db = installed.packages(), recursive = TRUE, which = c("Depends", "Imports", "LinkingTo"))))); info <- installed.packages(); wanted <- intersect(wanted, rownames(info)); fields <- intersect(c("Package", "Version", "Priority", "License", "Repository", "Built"), colnames(info)); write.table(info[sort(wanted), fields, drop = FALSE], row.names = FALSE, quote = TRUE, sep = "\t")' || return 1
  run_logged "$label-session-info" "$repository_root" "$rscript_binary" --vanilla -e 'cat(R.version.string, "\n"); cat("platform:", R.version$platform, "\n"); cat("testthat:", as.character(packageVersion("testthat")), "\n"); print(packageDescription("testthat")[intersect(c("Package", "Version", "License", "URL", "BugReports", "Repository", "Date/Publication", "Built"), names(packageDescription("testthat")))]); sessionInfo()' || return 1
  run_logged "$label-source-digests" "$repository_root" sha256sum "$package_dir/DESCRIPTION" "$package_dir/NAMESPACE" "$package_dir/R/probe.R" "$package_dir/tests/testthat.R" "$package_dir/tests/testthat/test-probe.R" || return 1
  run_logged "$label-build" "$build_dir" "$r_binary" CMD build --no-build-vignettes "$package_dir" || return 1
  tarball="$build_dir/statqedRToolchainProbe_0.0.0.9000.tar.gz"
  run_logged "$label-tarball-digest" "$repository_root" sha256sum "$tarball" || return 1
  run_logged "$label-check-tarball" "$check_dir" "$r_binary" CMD check --no-manual "$tarball" || return 1
  run_logged "$label-install-tarball" "$repository_root" "$r_binary" CMD INSTALL --library="$install_library" "$tarball" || return 1
  run_logged "$label-testthat" "$repository_root" "$rscript_binary" --vanilla -e 'library(testthat); testthat::test_local(commandArgs(TRUE)[1], reporter = "summary", stop_on_failure = TRUE)' "$package_dir" || return 1
  R_LIBS_USER="$install_library:$R_LIBS_USER" run_logged "$label-installed-smoke" "$repository_root" "$rscript_binary" --vanilla -e 'library(statqedRToolchainProbe); stopifnot(identical(unclass(probe_identity(11L)), 11L)); cat("installed smoke ok\n")' || return 1
}

rejection_probe() {
  local work_dir="$run_root/rejection"
  local mutated_dir="$work_dir/statqedRToolchainProbe"
  local build_dir="$work_dir/build"
  local check_dir="$work_dir/check"
  local install_library="$work_dir/install-library"
  local test_library="$work_dir/test-library"
  local tarball
  local status
  mkdir -p "$work_dir" "$build_dir" "$check_dir"
  cp -a "$package_dir" "$mutated_dir"
  sed -i 's/Depends: R (>= 4.4.0)/Depends: R (>= 4.7.0)/' "$mutated_dir/DESCRIPTION"
  export R_LIBS_USER="$test_library"
  export R_LIBS_SITE="$work_dir/empty-site-library"
  mkdir -p "$R_LIBS_SITE"
  export R_ENVIRON_USER=/dev/null
  export R_PROFILE_USER=/dev/null
  export TZ=UTC
  export LC_ALL=C.UTF-8
  run_logged rejection-dependency-source-install "$repository_root" prepare_dev_library "$test_library" || return 1
  run_logged rejection-mutated-description "$repository_root" sha256sum "$mutated_dir/DESCRIPTION" || return 1
  run_logged rejection-build "$build_dir" R CMD build --no-build-vignettes "$mutated_dir" || return 1
  tarball="$build_dir/statqedRToolchainProbe_0.0.0.9000.tar.gz"
  run_logged rejection-check-tarball "$check_dir" R CMD check --no-manual "$tarball"
  status=$?
  if [ "$status" -eq 0 ]; then
    printf '%s\n' 'Expected Depends: R incompatibility was not rejected.' >&2
    return 1
  fi
  mkdir -p "$install_library"
  run_logged rejection-install-tarball "$repository_root" R CMD INSTALL --library="$install_library" "$tarball"
  status=$?
  if [ "$status" -eq 0 ]; then
    printf '%s\n' 'Expected Depends: R incompatibility was installed.' >&2
    return 1
  fi
  return 0
}

capture_conda_lock() {
  # Retain SHA-256 fragments for every artifact in the solved environment,
  # not only mutable channel URLs.
  run_logged floor-conda-explicit-lock "$repository_root" conda list --prefix "$floor_prefix" --explicit --sha256
  run_logged floor-conda-explicit-lock-digest "$repository_root" sha256sum "$log_dir/floor-conda-explicit-lock.stdout"
  run_logged floor-conda-json-lock "$repository_root" conda list --prefix "$floor_prefix" --json
  run_logged floor-conda-selected-artifact-digests "$repository_root" sha256sum \
    "$state_root/pkgs/r-base-4.4.3-h14df4e6_4.conda" \
    "$state_root/pkgs/r-testthat-3.2.3-r44h3697838_2.conda"
}

recreate_floor_probe() {
  local source_lock="$log_dir/floor-conda-explicit-lock.stdout"
  local recreated_prefix="$state_root/recreated-r-4.4.3-$(date --utc +%Y%m%dT%H%M%S)-$RANDOM"
  [ -f "$source_lock" ] || {
    printf 'Missing SHA-256 explicit floor lock: %s\n' "$source_lock" >&2
    return 2
  }
  run_logged floor-conda-offline-recreate "$repository_root" conda create --offline --yes \
    --prefix "$recreated_prefix" --file "$source_lock" || return 1
  floor_prefix="$recreated_prefix"
  capture_conda_lock || return 1
  runtime_probe floor "$floor_prefix/bin/R" "$floor_prefix/bin/Rscript" floor
}

rejected_conda_development_probe() {
  local candidate_prefix="$state_root/rejected-r-4.6.1-$(date --utc +%Y%m%dT%H%M%S)-$RANDOM"
  run_logged development-conda-unsatisfied "$repository_root" conda create --dry-run --yes \
    --solver libmamba --override-channels -c conda-forge --prefix "$candidate_prefix" \
    'r-base=4.6.1' 'r-testthat=3.3.2'
  local status=$?
  if [ "$status" -eq 0 ]; then
    printf 'Expected unavailable conda R 4.6.1/testthat 3.3.2 combination resolved.\n' >&2
    return 1
  fi
  return 0
}

mode=${1:-all}
capture_host || exit 1
case "$mode" in
  development)
    runtime_probe development R Rscript dev
    ;;
  floor)
    [ -x "$floor_prefix/bin/R" ] || {
      printf 'Missing floor runtime: %s\n' "$floor_prefix/bin/R" >&2
      exit 2
    }
    capture_conda_lock || exit 1
    runtime_probe floor "$floor_prefix/bin/R" "$floor_prefix/bin/Rscript" floor
    ;;
  floor-recreate)
    recreate_floor_probe
    ;;
  conda-development-rejection)
    rejected_conda_development_probe
    ;;
  rejection)
    rejection_probe
    ;;
  all)
    runtime_probe development R Rscript dev || exit 1
    [ -x "$floor_prefix/bin/R" ] || {
      printf 'Missing floor runtime: %s\n' "$floor_prefix/bin/R" >&2
      exit 2
    }
    capture_conda_lock || exit 1
    runtime_probe floor "$floor_prefix/bin/R" "$floor_prefix/bin/Rscript" floor || exit 1
    rejection_probe || exit 1
    ;;
  *)
    printf 'usage: %s {all|development|floor|floor-recreate|conda-development-rejection|rejection}\n' "$0" >&2
    exit 64
    ;;
esac
