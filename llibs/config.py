from dotenv import load_dotenv
import os

load_dotenv()

JABBERDIR = os.getenv("JABBERDIR")
NOTIFICATIONBLOB = {"unread": 0, "by": []}
KEYBLOB = {"xmpp":"","key":""}
MNE = [] # list of users for who the "not encrypted" warning is shown
PGPABILITY = True # default is true because we want encryption by default
DEBUG = False # the only person that cares about the debug output is me
KEYPATHS = {"public": os.path.join(JABBERDIR, ".keys", "public")}
Passphrase = None

Helpmsg = """
Welcome to PurpleJabber. You can navigate with these:
    /help          /? - Shows this menu
    /quit          /! - Exit the client
    /delete           - Delete the client and all files for client.
             Be careful, you will be prompted once, not twice.
    /reboot        /@ - Reboot the client, clearing all cache & removing messages from RAM.
    /user          /^ - Chose who to message (/^ user@thesecure.biz)
    /contacts      /* - List contacts
    /add           /+ - Add a contact (/+ user@thesecure.biz)
    /remove        /- - Remove a contact (/- user@thesecure.biz)
    /notifications /% - Shows messages you missed while the client was open
    /pgp           /< - Enable/Disable PGP encrypted messages.
    /import        /> - Import a public PGP key pair (/> /path/to/key.asc)
    /debug         /; - Debug and show info-level logger information (you won't need this)
Pressing enter without any command will send a message to your most recent contact.
"""
#    /exec          /$ - Execute commands from inside PurpleJabber
#    /pullplugin    /ppl - Pull a plugin into your library
#    /plugin        /ipl - Install a plugin that's in your library