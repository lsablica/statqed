start=2026-08-03T13:01:44Z
end=2026-08-03T13:01:44Z
cwd=/tmp/statqed-preflight-9bf9922
exit_status=0
argv=Rscript --vanilla -e wanted\ \<-\ unique\(c\(\"testthat\"\,\ unlist\(tools::package_dependencies\(\"testthat\"\,\ db\ =\ installed.packages\(\)\,\ recursive\ =\ TRUE\,\ which\ =\ c\(\"Depends\"\,\ \"Imports\"\,\ \"LinkingTo\"\)\)\)\)\)\;\ info\ \<-\ installed.packages\(\)\;\ wanted\ \<-\ intersect\(wanted\,\ rownames\(info\)\)\;\ fields\ \<-\ intersect\(c\(\"Package\"\,\ \"Version\"\,\ \"Priority\"\,\ \"License\"\,\ \"Repository\"\,\ \"Built\"\)\,\ colnames\(info\)\)\;\ write.table\(info\[sort\(wanted\)\,\ fields\,\ drop\ =\ FALSE\]\,\ row.names\ =\ FALSE\,\ quote\ =\ TRUE\,\ sep\ =\ \"\\t\"\) 
