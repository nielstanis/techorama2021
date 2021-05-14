#/bin/bash
in-toto-record start --verbose --step create --key aimee
dotnet new console -n app
in-toto-record stop --verbose --step create --products app/Program.cs --key aimee

