import Nautilus from '../src/nautilus.js'


const delay = (s: number) => new Promise(resolve => setTimeout(resolve, s * 1000));

async function main() {

    let nautilus = new Nautilus();
    await nautilus.open()
    try {
        await nautilus.reset()
        console.log(`version: ${await nautilus.getVersion()}`)
        console.log(`mac: ${await nautilus.getMac()}`)
        console.log(`vin: ${await nautilus.getVin()} V`)
        console.log(`temp: ${await nautilus.getTemperature()} C`)
    }
    catch (err) {
        console.log(err) 
    }
    await nautilus.close()
}


main();