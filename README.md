# PurpleJabber
Jabber/XMPP client built with Python which utilizes PGP for encryption, removing the barrier for different XMPP servers using different encryption methods.

<img src="src/image.jpg"/>

## Installation

1. Clone the repo
```
git clone https://github.com/cyivor/purplejabber
```

3. Change directory
```
cd purplejabber
```

5. Install 3 dependencies
```
pip install slixmpp python-gnupg dotenv
```

4. Change the mode of `setup.sh`
```
chmod +x setup.sh
```

5. Run `setup.sh`

***Before running the setup script, look inside the file and change the value of `localPassword` to whatever you want your local password to be, and `passwordForDataFile` to a random string of text, or an AES key, or whatever you want really.***
```
./setup.sh
```

### Requirements

- Openssl
- Python3.13.2 (with Pip)
- Bash
- Linux machine/vm

## Future features

1. Version control command 
```
/version 1.0
```

2. Personalisation
```
/settings | /preferences
```

3. Plugins
```
/plugin <plugin_name> | /pullplugin <plugin_to_add>
```

4. Execute CLI commands
```
/exec uname -a
```

5. Encryption with XSalsa20 for secret pgp keys

---

<i>If there are any issues, please feel free to open them here on Github</i>

---

# Updates
```
2025.05.16.1 - Add Import (pgp key) command and fix setup.sh issue that prevented setup.sh from creating encrypted data file
2025.05.16.2 - Add ability to see debug output for the code
2025.05.17.1 - You can use the import command by its lonesome to find public pgp keys in your filesystem
```
