# PurpleJabber
Jabber/XMPP client built with Python which utilizes PGP for encryption, removing the barrier for different XMPP servers using different encryption methods.

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

***Before running the setup script, look inside the file and change the value of*** `localpassword` ***to whatever you want your local password to be***
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

---

<i>If there are any issues, please feel free to open them here on Github</i>

---

# Updates
```
2025.05.16 - Add Import (pgp key) command and fix setup.sh issue that prevented setup.sh from creating encrypted data file
```
