import Nautilus from '../src/nautilus.js'


const delay = (s: number) => new Promise(resolve => setTimeout(resolve, s * 1000));

async function main() {

    let nautilus = new Nautilus();
    await nautilus.open()
    try {
        await nautilus.reset()
        console.log(await nautilus.getVin())
        console.log(await nautilus.getTemperature())
    }
    catch (err) {
        console.log(err) 
    }
    await nautilus.close()
}


main();