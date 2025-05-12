if [ ! -f .env ]; then
  echo ".env not found"
  exit 1
fi
export $(grep -v '^#' .env | xargs)
if [ -z "$passwordForDataFile" ]; then
  echo "pass not found | .env"
  exit 1
fi
IFILE="$JABBERDIR/data.json"
OFILE="$JABBERDIR/data.pj"
openssl enc -chacha20 -salt -in "$IFILE" -out "$OFILE" -pass pass:"$passwordForDataFile"
if [ $? -eq 0 ]; then
  :
else
  echo 0
  exit 1
fi
sudo shred -u ${IFILE}
echo ${OFILE}
