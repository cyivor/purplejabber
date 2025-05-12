import subprocess, threading, os, json, sys
from llibs.config import JABBERDIR

class FileCryptHandler:
    def CryptMain(self, type_):
        res = None
        def exc_(cmd, rescontainer):
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=10)
                rescontainer['output'] = result.stdout.strip()
            except Exception as e:
                rescontainer['error'] = str(e)

        def Crypt():
            nonlocal res
            rescontainer = {}
            spath = os.path.join(JABBERDIR, "src", f"{type_}.sh")
            thread = threading.Thread(target=exc_, args=(f"/bin/bash {spath}", rescontainer))
            thread.start()
            thread.join()
            
            if 'error' in rescontainer:
                sys.exit(1)
            res = rescontainer.get('output', None)
            return res
        return Crypt()

    def TMPCreation(self, dat_, type_="decrypt"):
        returnData = None
        Path = self.CryptMain(type_) # type_ is "encrypt" or "decrypt" no other - returns path of file after encrypted/decrypted
        if type_ == "decrypt":
            with open(Path,"r") as f:
                data = json.load(f)
            returnData = data["dat_"][dat_]
            os.remove(Path)
        else:
            returnData = Path
        return returnData