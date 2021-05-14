from securesystemslib import interface
from in_toto.models.layout import Layout
from in_toto.models.metadata import Metablock

def main():
  # Load Niels's private key to later sign the layout
  key_niels = interface.import_rsa_privatekey_from_file("niels")
  # Fetch and load aimee's and noud's public keys
  # to specify that they are authorized to perform certain step in the layout
  key_aimee = interface.import_rsa_publickey_from_file("../functionary_aimee/aimee.pub")
  key_noud = interface.import_rsa_publickey_from_file("../functionary_noud/noud.pub")

  layout = Layout.read({
      "_type": "layout",
      "keys": {
          key_aimee["keyid"]: key_aimee,
          key_noud["keyid"]: key_noud,
      },
      "steps": [{
          "name": "create",
          "expected_materials": [],
          "expected_products": [["CREATE", "app/Program.cs"], ["DISALLOW", "*"]],
          "pubkeys": [key_aimee["keyid"]],
          "expected_command": [
              "dotnet",
              "new",
              "console",
              "-n",
              "app"
          ],
          "threshold": 1,
        },{
          "name": "publish",
          "expected_materials": [
            ["MATCH", "app/Program.cs", "WITH", "PRODUCTS", "FROM",
             "create"], ["DISALLOW", "*"],
          ],
          "expected_products": [["CREATE", "published/app"], ["CREATE", "published/app.*"], ["DISALLOW", "*"]],
          "pubkeys": [key_noud["keyid"]],
          "expected_command": [
              "dotnet",
              "publish",
              "-o",
              "published",
              "app"
          ],
          "threshold": 1,
        },{
          "name": "package",
          "expected_materials": [
            ["MATCH", "published/*", "WITH", "PRODUCTS", "FROM",
             "publish"], ["DISALLOW", "*"],
          ],
          "expected_products": [
              ["CREATE", "published.tar.gz"], ["DISALLOW", "*"],
          ],
          "pubkeys": [key_noud["keyid"]],
          "expected_command": [
              "tar",
              "-zcvf",
              "published.tar.gz",
              "published",
          ],
          "threshold": 1,
        }],
      "inspect": [{
          "name": "untar",
          "expected_materials": [
              ["MATCH", "published.tar.gz", "WITH", "PRODUCTS", "FROM", "package"],
              # FIXME: If the routine running inspections would gather the
              # materials/products to record from the rules we wouldn't have to
              # ALLOW other files that we aren't interested in.
              ["ALLOW", ".keep"],
              ["ALLOW", "niels.pub"],
              ["ALLOW", "root.layout"],
              ["DISALLOW", "*"]
          ],
          "expected_products": [
              ["MATCH", "published/*", "WITH", "PRODUCTS", "FROM", "publish"],
              # FIXME: See expected_materials above
              ["ALLOW", "published/app.*"],
              ["ALLOW", "published.tar.gz"],
              ["ALLOW", ".keep"],
              ["ALLOW", "niels.pub"],
              ["ALLOW", "root.layout"],
              ["DISALLOW", "*"]
          ],
          "run": [
              "tar",
              "xzf",
              "published.tar.gz",
          ]
        }],
  })

  metadata = Metablock(signed=layout)

  # Sign and dump layout to "root.layout"
  metadata.sign(key_niels)
  metadata.dump("root.layout")

if __name__ == '__main__':
  main()
