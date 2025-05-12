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

4. Run `setup.sh`
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
3. Create, remove, certify, and identify PGP key pairs
```
/cpgp create/remove/certify/find
```
5. Personalisation
```
/settings | /preferences
```

---

<i>If there are any issues, please feel free to open them here on Github</i>
