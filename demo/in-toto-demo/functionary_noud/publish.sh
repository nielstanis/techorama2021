#/bin/bash
in-toto-record start --verbose --step publish --materials app/Program.cs --key noud
dotnet publish -o published app
in-toto-record stop --verbose --step publish --products published/* --key noud
