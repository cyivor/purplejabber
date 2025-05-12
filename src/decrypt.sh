rndm() {
  local length=$1
  rndmstr=$(tr -dc 'a-zA-Z' < /dev/urandom | fold -w "$length" | head -n 1)
  rndmstr="${rndmstr//$'\n'/}"
}
if [ ! -f .env ]; then
  echo ".env not found"
  exit 1
fi
export $(grep -v '^#' .env | xargs)
if [ -z "$passwordForDataFile" ]; then
  echo "pass not found | .env"
  exit 1
fi
rndm 6
IFILE="$JABBERDIR/data.pj"
OFILE="/tmp/${rndmstr}.json"
openssl enc -d -chacha20 -in "$IFILE" -out "$OFILE" -pass pass:"$passwordForDataFile"
if [ $? -eq 0 ]; then
  :
else
  echo 0
  exit 1
fi
echo ${OFILE}