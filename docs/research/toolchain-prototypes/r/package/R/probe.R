#' Construct a toolchain-probe value
#'
#' This helper exists only to exercise package loading and test execution. It
#' does not define a StatQED semantic or serialization type.
#'
#' @param value One integer value.
#' @return An integer carrying the disposable `statqed_r_probe` class.
#' @export
probe_identity <- function(value) {
  if (!is.integer(value) || length(value) != 1L || is.na(value)) {
    stop("`value` must be one non-missing integer", call. = FALSE)
  }

  structure(value, class = c("statqed_r_probe", "integer"))
}
