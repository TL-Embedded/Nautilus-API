import Nautilus from '../src/nautilus.js'


const delay = (s: number) => new Promise(resolve => setTimeout(resolve, s * 1000));

async function main() {

    let nautilus = new Nautilus();
    await nautilus.open()
    try {
        console.log(await nautilus.getMac())
    }
    catch (err) {
        console.log(err) 
    }
    await nautilus.close()
}


main();