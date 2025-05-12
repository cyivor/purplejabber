from llibs.config import JABBERDIR
import os, json

class ContactManager:
    def __init__(self, cryptHandlerInstance):
        self.fileCryptHandler = cryptHandlerInstance

    def _read_all_data(self):
        # renamed from old version because looks better + improved functionality
        decryptedPath = self.fileCryptHandler.CryptMain("decrypt")
        if decryptedPath is None or not os.path.exists(decryptedPath):
            return None
        try:
            with open(decryptedPath, "r") as f:
                data = json.load(f)
            return data
        except Exception as e:
            return None
        finally:
            if decryptedPath and os.path.exists(decryptedPath):
                try:
                    os.remove(decryptedPath)
                except OSError:
                    pass

    def _write_all_data(self, dataToWrite):
            
        FullPath = os.path.join(JABBERDIR, "data.json")
        try:
            with open(FullPath, "w+") as NewDataFile:
                json.dump(dataToWrite, NewDataFile, indent=4)
            self.fileCryptHandler.CryptMain("encrypt")
            return True
        except Exception as e:
            return False


    def QueryLocalPassword(self, passAttempt):
        if passAttempt != self.fileCryptHandler.TMPCreation("localPassword", "decrypt"): return False
        return True

    def GetContacts(self):
        contacts = self.fileCryptHandler.TMPCreation("list", "decrypt")
        return contacts if contacts is not None else []

    def GetRecentRecipient(self):
        recipient = self.fileCryptHandler.TMPCreation("lastRecipient", "decrypt")
        return recipient

    def RemoveContact(self, XMPPAddress):
        data = self._read_all_data()
        if XMPPAddress in data["dat_"]["list"]:
            data["dat_"]["list"].remove(XMPPAddress)
            self._write_all_data(data)
            return True
        return False

    def AddRecentRecipient(self, Recipient):
        data = self._read_all_data()
        data["dat_"]["lastRecipient"] = Recipient
        self._write_all_data(data)
        return True

    def AddContact(self, XMPPAddress):
        data = self._read_all_data()
        if XMPPAddress not in data["dat_"]["list"]:
            data["dat_"]["list"].append(XMPPAddress)
            self._write_all_data(data)
            return True
        return False