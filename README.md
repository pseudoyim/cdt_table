# CDT table

Scrapes CDT package namespaces and tabulates them (for inventory/survey purposes).

Steps:
1. Pull repodata from channels and searches for packages ending with the CDT suffixes (OS-ARCH).
2. Make a df with an index column of just the CDT names (e.g. "libx11-devel").
3. Iteratively LEFT JOIN all of the suffixes' CDT names onto the index column.