test_that("the probe preserves an exact integer", {
  value <- probe_identity(7L)

  expect_identical(unclass(value), 7L)
  expect_s3_class(value, "statqed_r_probe")
})

test_that("unsupported values fail explicitly", {
  expect_error(probe_identity(7), "one non-missing integer", fixed = TRUE)
  expect_error(probe_identity(c(1L, 2L)), "one non-missing integer", fixed = TRUE)
  expect_error(probe_identity(NA_integer_), "one non-missing integer", fixed = TRUE)
})
