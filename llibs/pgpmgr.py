import gnupg, os, re, sys, getpass, shutil, subprocess
import llibs.config as config

class PGPManager:
    def __init__(self, cryptHandlerInstance, contactmgr):
        self.fileCryptHandler = cryptHandlerInstance
        self.contactmgr = contactmgr

    def ImportKey(self, keyPath=None):
        if not keyPath:
            Keys = self.FindKeys()
            print(f"{len(Keys)} keys found. ")
            for Index, KeyPath in enumerate(Keys):
                print(f"\n{Index + 1}) {KeyPath}")
            decision = input(": ")
            while decision > len(Keys) or decision < len(Keys):
                print("Invalid number. Try again.")
                decision = input(": ")
            SelectKey = Keys[decision - 1]
        else:
            SelectKey = keyPath
        if os.path.exists(SelectKey):
            contact = None
            keyShort = keyPath.split("/")[-1]
            FullKey = os.path.join(config.KEYPATHS["public"], keyShort)
            print(f"Importing {keyShort}")
            shutil.copyfile(SelectKey, FullKey, follow_symlinks=False)
            print("Imported.")
            print("Attempting to find match for key.")
            matchFound, contact = self.FindMatch(FullKey)
            if matchFound: print(f"Successfully connected PGP key to {contact}")
            else:
                print(f"Unsuccessful in connected PGP key to {contact}")
                contact = input("Please enter a contact: ")
                keyAdded = self.AddKey(contact, FullKey)
                if keyAdded: print(f"Successfully connected PGP key to {contact}")
                else: print(f"Unsuccessful in connected PGP key to {contact}")
        else:
            print(f"Can't find that PGP key, please try again.")

    def FindKeys(self):
        keys = []
        
        if not hasattr(config, 'JABBERDIR') or not config.JABBERDIR:
            return []
            
        JABBERDIR = os.path.abspath(config.JABBERDIR)

        cmd = [
            'find', '/',
            '-path', JABBERDIR, '-prune',
            '-o',
            '-type', 'f',
            '-name', '*.asc',
            '-print'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
        if result.returncode == 0:
            if result.stdout:
                keys = [line for line in result.stdout.splitlines() if line]
            
        return keys

    def IsEncrypted(self, message):
        message = message.strip()
        messagePattern = re.compile(
            r"-----BEGIN PGP MESSAGE-----(.*?)-----END PGP MESSAGE-----",
            re.DOTALL
        )
        match = messagePattern.search(message)
        return bool(match)

    def FindMatch(self, XMPPAddressKey):
        Contacts = self.contactmgr.GetContacts()
        gContact = None
        for contact in Contacts:
            if contact.split("@")[0] in XMPPAddressKey:
                print(f"Matched {contact} with {XMPPAddressKey.split('/')[-1]}.")
                print("Connecting key to contact.")
                keyAdded = self.AddKey(contact, XMPPAddressKey)
                if keyAdded:
                    return True, contact
                else:
                    gContact = contact
                    break
        return False, gContact
                

    def AddKey(self, XMPPAddress, XMPPAddressKey):
        KeyData = self.contactmgr._read_all_data()
        PubKeys = KeyData["dat_"]["keys"]["public"]
        keyObj = config.KEYBLOB
        keyObj["xmpp"] = XMPPAddress
        keyObj["key"] = XMPPAddressKey
        PubKeys.append(keyObj)
        return self.contactmgr._write_all_data(KeyData)

    def GetKey(self, XMPPAddress):
        KeyData = self.fileCryptHandler.TMPCreation("keys", "decrypt")
        PubKeys = KeyData["public"]
        keyFile = None
        for key in PubKeys:
            if str(key["xmpp"]) == XMPPAddress:
                KeyFileName = str(key["key"])
                keyFile = KeyFileName + ".asc" if not KeyFileName.endswith(".asc") else KeyFileName
                break
        
        if keyFile is None:
            return False
        
        fullKeyPath = os.path.join(config.KEYPATHS["public"], keyFile)
        return fullKeyPath

    def DecryptMessage(self, EncryptedMessage):
        gpg = gnupg.GPG()
        gpg.encoding = 'utf-8'

        DecryptedData = gpg.decrypt(EncryptedMessage, passphrase=config.Passphrase)

        attempts = 0
        while not DecryptedData.ok:
            attempts += 1
            PassphraseAttempt = getpass.getpass(f"Please enter your PGP passphrase ({attempts}/5): ")
            
            DecryptedData = gpg.decrypt(
                EncryptedMessage,
                passphrase=PassphraseAttempt
            )
            if DecryptedData.ok:
                config.Passphrase = PassphraseAttempt
                break
            if attempts >= 5:
                print("You have attempted to decrypt messages not meant for you, goodbye.")
                sys.exit(0) 
        
        if DecryptedData.ok:
            return str(DecryptedData)
        else:
            # this path should literally not be reached
            # print(f"{DecryptedData.status} | {DecryptedData.stderr}")
            return None

    def EncryptMessage(self, keyFilePath, message):
        if not os.path.exists(keyFilePath):
            return "This user is using the PurpleJabber CLI client. They are unable to resolve the public PGP key associated with your Jabber address."

        try:
            with open(keyFilePath, 'r', encoding='utf-8') as f:
                pubKeyData = f.read()
        except Exception as e:
            return f"Error reading public key file: {str(e)}"

        gpg = gnupg.GPG()
        gpg.encoding = 'utf-8'

        res = gpg.import_keys(pubKeyData)
        if not res or not res.fingerprints:
            return None 

        fingerprint = res.fingerprints[0]

        EncryptedDataObj = gpg.encrypt(
            message,
            recipients=[fingerprint],
            always_trust=True
        )

        if EncryptedDataObj.ok:
            return str(EncryptedDataObj)
        else:
            return EncryptedDataObj.stderr