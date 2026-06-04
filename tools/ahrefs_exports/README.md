# Ahrefs exports — drop folder

Each week, export from Ahrefs **Referring Domains** (or Backlinks) → **CSV** and
save the file here (any filename ending in `.csv`). The Monday scheduled task
("weekly-lost-backlinks") picks up the **newest** CSV in this folder, diffs it
against last week's snapshot, and surfaces a summary of lost high-DR domains.

Free Backlink Checker has no CSV export — this needs an Ahrefs account/plan that
allows export, or paste the data into a CSV with `Domain,Domain rating` columns.
