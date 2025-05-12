import slixmpp, asyncio, sys, getpass, gc, os
import llibs.config as app_config 

from llibs.config import Helpmsg
from llibs.crypt import FileCryptHandler
from llibs.pgpmgr import PGPManager
from llibs.notificationmgr import NotificationManager
from llibs.contactmgr import ContactManager

class XMPPClient(slixmpp.ClientXMPP):
    def __init__(self, jid, password, fileCryptHandler, pgpmgr, notificationmgr, contactmgr):
        super().__init__(jid, password)

        self.fileCryptHandler = fileCryptHandler
        self.pgpmgr = pgpmgr
        self.notificationmgr = notificationmgr
        self.contactmgr = contactmgr
        
        self.add_event_handler("session_start", self.session_start_handler) # renamed it
        self.add_event_handler("message", self.message_received_handler)

        self.running = True

    async def session_start_handler(self, event): # rename too
        self.send_presence()
        await self.get_roster()
        print(Helpmsg)

        asyncio.create_task(self.input_loop())

    async def input_loop(self):
        while self.running:
            try:
                command = await asyncio.to_thread(input, ": ")
                match command:
                    case _ if command.startswith("/delete"):
                        prompt = input("Are you sure you want to delete PurpleJabber and it's files permanently? [y/n]: ").lower()
                        if prompt in ["y",""]:
                            password = getpass.getpass("Enter your local password: ")
                            if self.contactmgr.QueryLocalPassword(password):
                                if app_config.JABBERDIR:
                                    uninstallScript = os.path.join(app_config.JABBERDIR, "src", "uninstall.sh")
                                    if os.path.isfile(uninstallScript):
                                        os.execv("/bin/bash", ["/bin/bash", uninstallScript])
                                    else:
                                        print(f"Uninstall script not found at {uninstallScript}")
                                else:
                                    print("JABBERDIR not configured, cannot run uninstall script.")
                            else:
                                print("Password was incorrect.")
                        elif prompt != "n":
                            print(f"{prompt} is not a valid option.")

                    case _ if command.startswith("/quit") | command.startswith("/!"):
                        print("Exiting")
                        self.running = False
                        self.disconnect()
                        break
                    case _ if command.startswith("/reboot") | command.startswith("/@"):
                        gc.collect()
                        pye = sys.executable
                        self.running = False
                        self.disconnect()
                        os.execv(pye, ['python'] + sys.argv)
                        break
                    case _ if command.startswith("/user") | command.startswith("/^"):
                        parts = command.split(maxsplit=1)
                        recipient = parts[1] if len(parts) > 1 else None
                        if recipient:
                            if recipient in self.contactmgr.GetContacts():
                                print(f"Recipient set to {recipient}")
                                self.contactmgr.AddRecentRecipient(recipient)
                            else:
                                print(f"{recipient} is not in your contacts. Do /* to check your contacts.")
                        else:
                            print("You need to set a recipient (e.g., /^ user@thesecure.biz)")
                    case _ if command.startswith("/contacts") | command.startswith("/*"):
                        contacts = self.contactmgr.GetContacts()
                        if contacts:
                            print("\n".join(contacts))
                        else:
                            print("No contacts found.")
                    case _ if command.startswith("/add") | command.startswith("/+"):
                        parts = command.split(maxsplit=1)
                        xmppaddress = parts[1] if len(parts) > 1 else None
                        if xmppaddress:
                            if self.contactmgr.AddContact(xmppaddress):
                                print(f"{xmppaddress} added to your contacts.")
                            else:
                                print(f"Failed to add {xmppaddress} for contacts.")
                        else:
                            print("Please specify a Jabber address to add (e.g., /+ user@thesecure.biz)")
                    case _ if command.startswith("/remove") | command.startswith("/-"):
                        parts = command.split(maxsplit=1)
                        xmppaddress = parts[1] if len(parts) > 1 else None
                        if xmppaddress:
                            if self.contactmgr.RemoveContact(xmppaddress):
                                print(f"{xmppaddress} removed from contacts.")
                            else:
                                print(f"{xmppaddress} not found in contacts or failed to remove.")
                        else:
                            print("Please specify an XMPP address to remove (e.g., /- user@thesecure.biz)")
                    case _ if command.startswith("/notifications") | command.startswith("/%"):
                        parts = command.split(maxsplit=1)
                        xmppaddress = parts[1] if len(parts) > 1 else None
                        if xmppaddress is None:
                            self.notificationmgr.RetrieveNotifications()
                        else:
                            messages = self.notificationmgr.RetrieveBlobs(xmppaddress)
                            print(messages)
                    case _ if command.startswith("/pgp") | command.startswith("/<"):
                        app_config.PGPABILITY = not app_config.PGPABILITY
                        status = " " if app_config.PGPABILITY else " not "
                        print(f"Your messages will{status}be encrypted from now on.")
                    case _ if command.startswith("/help") | command.startswith("/?"):
                        print(Helpmsg)
                    case _ if not command.startswith("/"):
                        message = command
                        recipient = self.contactmgr.GetRecentRecipient()
                        if recipient and recipient in self.contactmgr.GetContacts():
                            finalMessage = message
                            if app_config.PGPABILITY:
                                KeyPath = self.pgpmgr.GetKey(recipient)
                                if not KeyPath:
                                    print(f"No public PGP key for {recipient}. Sending messages unencrypted for now.")
                                    app_config.PGPABILITY = False 
                                else:
                                    encryptedMessage = self.pgpmgr.EncryptMessage(KeyPath, message)
                                    if encryptedMessage and "-----BEGIN PGP MESSAGE-----" in encryptedMessage:
                                        finalMessage = encryptedMessage
                                    else:
                                        print(f"PGP encryption failed. Sending unencrypted.")
                            self.send_message(mto=recipient, mbody=finalMessage, mtype='chat')
                            print(f"➝")
                        else:
                            if not recipient: print("No recipient selected. Use /^ to set one.")
                            else: print(f"{recipient} not in contacts.")

            except KeyboardInterrupt:
                print("\nExiting by user request.")
                self.running = False
                self.disconnect()
                break
            except EOFError:
                print("\nInput stream closed. Exiting.")
                self.running = False
                self.disconnect()
                break
            except Exception as e:
                print(f"An error occurred in input loop: {e}")


    def message_received_handler(self, msg): # add _handler* compared to old
        userJIDFull = str(msg['from'])
        # client = userJIDFull.split("/")[1]
        # leaving this here for any devs that wanna poke lol
        user = userJIDFull.split("/")[0]
        message = str(msg['body'])

        if self.pgpmgr.IsEncrypted(message):
            decrypted_result = self.pgpmgr.DecryptMessage(message)
            if decrypted_result is not None:
                message = decrypted_result
            else:
                print(f"\nFailed to decrypt PGP message from {user}.")
                if user not in app_config.MNE: app_config.MNE.append(user)
        elif user not in app_config.MNE:
             print(f"\nMessage from {user} is not encrypted. Be careful.")
             app_config.MNE.append(user) # Add to MNE to warn only once per session

        current_recipient = self.contactmgr.GetRecentRecipient()
        if current_recipient != user:
            self.notificationmgr.CreateBlob(user, message)
            if app_config.NOTIFICATIONBLOB["unread"] in [1, 10, 20, 50]:
                 print(f"\nYou have {app_config.NOTIFICATIONBLOB['unread']} unread messages. Type /% to read.")
        else:
            print(f"\n{user}: {message}")
            print(": ", end="", flush=True)

def main():
    if not app_config.JABBERDIR or not os.path.isdir(app_config.JABBERDIR):
        print("JABBERDIR environment variable is not set or points to an invalid directory.")
        print("Please set JABBERDIR to the root directory of your PurpleJabber client.")
        sys.exit(1)
        
    fileCryptHandler = FileCryptHandler()
    pgpmgr = PGPManager(fileCryptHandler)
    contactmgr = ContactManager(fileCryptHandler)
    notificationmgr = NotificationManager()

    localPasswordAttempt = getpass.getpass("Enter local password: ")
    if not contactmgr.QueryLocalPassword(localPasswordAttempt):
        print("Incorrect.")
        sys.exit(1)
    
    JID = input("Enter your JID (e.g., user@thesecure.biz): ")
    if not (JID.endswith("@thesecure.biz") or JID.endswith("@xmpp.jp")):
        print("Invalid JID domain. Only thesecure.biz or xmpp.jp servers are allowed.")
        sys.exit(1)

    JIDPassword = getpass.getpass("Enter your JID password: ")

    xmppClient = XMPPClient(JID, JIDPassword, 
                             fileCryptHandler, pgpmgr, 
                             notificationmgr, contactmgr)
    try:
        xmppClient.connect()
        xmppClient.process(forever=False)
    
    except slixmpp.exceptions.SASLMutualAuthFailed:
        print("Authentication failed: Incorrect JID password.")
    except slixmpp.exceptions.SASLNoAcceptableMechanism:
         print("Authentication failed: No acceptable SASL mechanism. Check server/client capabilities.")
    except ConnectionRefusedError:
        print("Connection refused. Ensure the XMPP server is running and accessible.")
    except OSError as e: # Catch socket errors, DNS issues etc.
        print(f"Network or OS error during connection: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # print("disconnecting") # for debugging
        if hasattr(xmppClient, 'socket') and xmppClient.socket and not xmppClient.socket.is_closed:
             xmppClient.disconnect()
        # print("done") # also for debugging