npm update
rm -r package/*
tsc --declaration
cp package.json ./package/package.json
cd ./package && npm publish --access public