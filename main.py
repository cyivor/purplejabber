import slixmpp, asyncio, sys, getpass, gc, os, logging

import llibs.config as app_config

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
        
        self.add_event_handler("session_start", self.sessionHandler)
        self.add_event_handler("message", self.messageReceivedHandler)
        self.add_event_handler("presence_subscribe", self.handleSubscription)
        self.add_event_handler("roster_update", self.handleRoster)

        self.running = True

    async def handleRoster(self, iq):
        return

    async def handleSubscription(self, pres):
        return

    async def sessionHandler(self, event):
        self.send_presence()
        await self.get_roster()
        print(app_config.Helpmsg)

        asyncio.create_task(self.inputLoop())

    async def inputLoop(self):
        while self.running:
            try:
                command = await asyncio.to_thread(input, ": ")
                
                if not command.strip():
                    continue
                
                commandParts = command.split(maxsplit=1)
                mainCommand = commandParts[0].lower()

                match mainCommand:
                    case "/delete":
                        prompt = await asyncio.to_thread(input, "Are you sure you want to delete PurpleJabber and it's files permanently? [y/n]: ")
                        prompt = prompt.lower()
                        if prompt in ["y",""]:
                            password = await asyncio.to_thread(getpass.getpass, "Enter your local password: ")
                            if self.contactmgr.QueryLocalPassword(password):
                                if app_config.JABBERDIR:
                                    uninstallScript = os.path.join(app_config.JABBERDIR, "src", "uninstall.sh")
                                    if os.path.isfile(uninstallScript):
                                        print("Attempting to run uninstall script...")
                                        os.execv("/bin/bash", ["/bin/bash", uninstallScript])
                                        self.running = False
                                        self.disconnect()
                                        await asyncio.sleep(0.5)
                                    else:
                                        print(f"Uninstall script not found at {uninstallScript}")
                                else:
                                    print("JABBERDIR not configured, cannot run uninstall script.")
                            else:
                                print("Password was incorrect.")
                        elif prompt != "n":
                            print(f"{prompt} is not a valid option.")

                    case "/quit" | "/!":
                        print("Exiting")
                        self.running = False
                        self.disconnect()
                        break
                    case "/reboot" | "/@":
                        print("Rebooting...")
                        logging.info("reboot initiated")
                        gc.collect()
                        pye = sys.executable
                        self.running = False

                        logging.info("calling disconnect")
                        self.disconnect() 
                        
                        logging.info("awaiting disconnect")
                        await self.disconnected 
                        logging.info("disconnected client")
                        
                        logging.info(f"replace process")
                        try:
                            os.execv(pye, [pye] + sys.argv)
                            logging.error("os.execv call returned, failed to replace the process") 
                        except OSError as oe:
                            logging.error(oe, exc_info=True)
                        except Exception as ex:
                            logging.error(ex, exc_info=True)
                        break
                    case "/user" | "/^":
                        recipient = commandParts[1] if len(commandParts) > 1 else None
                        if recipient:
                            if recipient in self.contactmgr.GetContacts():
                                print(f"Recipient set to {recipient}")
                                self.contactmgr.AddRecentRecipient(recipient)
                            else:
                                print(f"{recipient} is not in your contacts. Do /* to check your contacts.")
                        else:
                            print("You need to set a recipient (e.g., /^ user@thesecure.biz)")
                    case "/contacts" | "/*":
                        contacts = self.contactmgr.GetContacts()
                        if contacts:
                            print("\n".join(contacts))
                        else:
                            print("No contacts found.")
                    case "/add" | "/+":
                        xmppaddress = commandParts[1] if len(commandParts) > 1 else None
                        if xmppaddress:
                            if self.contactmgr.AddContact(xmppaddress):
                                print(f"{xmppaddress} added to your contacts.")
                            else:
                                print(f"Failed to add {xmppaddress} for contacts.")
                        else:
                            print("Please specify a Jabber address to add (e.g., /+ user@thesecure.biz)")
                    case "/remove" | "/-":
                        xmppaddress = commandParts[1] if len(commandParts) > 1 else None
                        if xmppaddress:
                            if self.contactmgr.RemoveContact(xmppaddress):
                                print(f"{xmppaddress} removed from contacts.")
                                self.send_presence_subscription(pto=xmppaddress, stype='unsubscribe')
                                self.del_roster_item(xmppaddress)
                            else:
                                print(f"{xmppaddress} not found in contacts or failed to remove.")
                        else:
                            print("Please specify an XMPP address to remove (e.g., /- user@thesecure.biz)")
                    case "/notifications" | "/%":
                        xmppaddress = commandParts[1] if len(commandParts) > 1 else None
                        if xmppaddress is None:
                            self.notificationmgr.RetrieveNotifications()
                        else:
                            messages = self.notificationmgr.RetrieveBlobs(xmppaddress)
                            print(messages)
                    case "/pgp" | "/<":
                        app_config.PGPABILITY = not app_config.PGPABILITY
                        status = " " if app_config.PGPABILITY else " not "
                        print(f"Your messages will{status}be encrypted from now on.")
                    case "/help" | "/?":
                        print(app_config.Helpmsg)
                    case "/import" | "/>":
                        xmppaddress = commandParts[1] if len(commandParts) > 1 else None
                        if not xmppaddress: self.pgpmgr.ImportKey()
                        else: self.pgpmgr.ImportKey(xmppaddress)
                    case "/debug" | "/;":
                        app_config.DEBUG = not app_config.DEBUG
                        status = " " if app_config.DEBUG else " not "
                        print(f"You will{status}view debug output")
                    case "/exec" | "/$":
                        ... # do tomorrow
                            # also fix /delete
                            # on top of that fix self.pgpmgr.FindKeys()
                    case _:
                        message = command
                        recipient = self.contactmgr.GetRecentRecipient()
                        if recipient and recipient in self.contactmgr.GetContacts():
                            finalMessage = message
                            if app_config.PGPABILITY:
                                KeyPath = self.pgpmgr.GetKey(recipient)
                                if not KeyPath:
                                    print(f"No public PGP key for {recipient}. Sending messages unencrypted for now.")
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
                logging.error(e, exc_info=True)


    def messageReceivedHandler(self, msg):
        if msg['type'] in ('chat', 'normal'):
            user = msg['from'].bare 
            message = str(msg['body'])

            if self.pgpmgr.IsEncrypted(message):
                decrypted = self.pgpmgr.DecryptMessage(message)
                if decrypted is not None:
                    message = decrypted
                else:
                    print(f"\nFailed to decrypt PGP message from {user}. This is probably because you haven't exported your private key to somewhere in your filesystem.")
                    if user not in app_config.MNE: app_config.MNE.append(user)
            elif user not in app_config.MNE:
                 print(f"\nMessage from {user} is not encrypted. Be careful.")
                 app_config.MNE.append(user)

            recipient = self.contactmgr.GetRecentRecipient()
            if recipient != user:
                self.notificationmgr.CreateBlob(user, message)
                unread = app_config.NOTIFICATIONBLOB.get("unread", 0)
                if unread in [1, 10, 20, 50] or (unread > 0 and unread % 5 == 0):
                     print(f"\nYou have {unread} unread messages. Type /% to read.")
                     print(": ", end="", flush=True)
            else:
                print(f"\n{user}: {message}")
                print(": ", end="", flush=True)

async def amain():
    if not app_config.JABBERDIR or not os.path.isdir(app_config.JABBERDIR):
        print("JABBERDIR environment variable is not set or points to an invalid directory.")
        print("Please set JABBERDIR to the root directory of your PurpleJabber client.")
        sys.exit(1)
        
    fileCryptHandler = FileCryptHandler()
    contactmgr = ContactManager(fileCryptHandler)
    pgpmgr = PGPManager(fileCryptHandler, contactmgr)
    contactmgr = ContactManager(fileCryptHandler)
    notificationmgr = NotificationManager()

    localPasswordAttempt = getpass.getpass("Enter local password: ")
    if not contactmgr.QueryLocalPassword(localPasswordAttempt):
        print("Incorrect.")
        sys.exit(1)
    
    JID = input("Enter your JID (e.g., user@thesecure.biz): ")
    """if not (JID.endswith("@thesecure.biz") or JID.endswith("@xmpp.jp")):
        print("Invalid JID domain. Only thesecure.biz or xmpp.jp servers are allowed.")
        sys.exit(1)"""

    JIDPassword = getpass.getpass("Enter your JID password: ")

    xmppClient = XMPPClient(JID, JIDPassword, 
                             fileCryptHandler, pgpmgr, 
                             notificationmgr, contactmgr)
    
    # added
    xmppClient.register_plugin('xep_0030')
    xmppClient.register_plugin('xep_0045') # multiuser chat
    xmppClient.register_plugin('xep_0199')

    try:
        await xmppClient.connect()
        await xmppClient.disconnected
    
    except ConnectionRefusedError:
        logging.error("Connection refused. Ensure the XMPP server is running", exc_info=True)
    except OSError as e:
        logging.error(f"Network or OS error during connection: {e}", exc_info=True)
    except Exception as e:
        logging.error(e, exc_info=True)
    finally:
        if hasattr(xmppClient, 'is_connected') and xmppClient.is_connected:
             xmppClient.disconnect()

if __name__ == '__main__':
    if app_config.DEBUG: logging.basicConfig(level=logging.INFO, format='%(levelname)-8s %(message)s')
    
    try:
        asyncio.run(amain())
    except KeyboardInterrupt:
        print("\nApplication interrupted. Exiting.")
    finally:
        logging.info("Application shutdown complete.")
