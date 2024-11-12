import os

print([
                {
                    "name":f,
                    "destination":"ok",
                    "creation_date": "date",
                    "size": f"{os.path.getsize("Input/"+f)} bytes"
                }
                for f in os.listdir("Input/")
            ])