chmod +x src/*
touch .env
echo "passwordForDataFile=ChangeThisDefaultPassword12345}!@£?£" > .env
echo "JABBERDIR=${PWD}" >> .env
echo '{"dat_":{"lastRecipient":"","localPassword":"ChangeThisToWhateverYouWantYourLocalPasswordToBe","list":[],keys:{"public":{}}}}' > data.json
./src/encrypt