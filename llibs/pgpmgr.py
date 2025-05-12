import gnupg, os, re, sys, getpass
import llibs.config as config

class PGPManager:
    def __init__(self, cryptHandlerInstance):
        self.fileCryptHandler = cryptHandlerInstance

    def IsEncrypted(self, message):
        message = message.strip()
        messagePattern = re.compile(
            r"-----BEGIN PGP MESSAGE-----(.*?)-----END PGP MESSAGE-----",
            re.DOTALL
        )
        match = messagePattern.search(message)
        return bool(match)

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