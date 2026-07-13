npm update
rm -r package/*
npx tsc --declaration
cp package.json ./package/package.json
cd ./package && npm publish --access public