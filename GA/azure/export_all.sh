for c in Families Operators Corpora Tasks Evaluation Nodes Models; do mongoexport  -d local -c $c -o $c.json; done
