#/bin/bash
in-toto-record start --verbose --step package --materials published/* --key noud
tar -zcvf published.tar.gz published
in-toto-record stop  --verbose --step package --products published.tar.gz --key noud
