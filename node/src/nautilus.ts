import { Scpi, fromUri } from './scpi.js'
import { SerialPort } from 'serialport';

class Nautilus {

    scpi: Scpi;
    private serialBuffer: Buffer;

    constructor (uri: string = "tcp://nautilus.local") {
        this.scpi = fromUri(uri);
        this.serialBuffer = Buffer.alloc(0);
    }

    async open() {
        await this.scpi.open();

        try {
            await this.isPresent(true)
        }
        catch (err) {
            // If we get an error during open, we really want to leave the transport closed.
            await this.scpi.close()
            throw err;
        }
    }

    async close() {
        await this.reset()
        await this.scpi.close()
    }

    async isPresent(throwOnError: boolean = false): Promise<boolean> {
        const success = (await this.scpi.getIdn()).startsWith("TL Embedded, Nautilus,")
        if (throwOnError && !success) {
            throw new Error("Nautilus not found")
        }
        return success;
    }

    async reset() {
        await this.scpi.write("*RST");
    }

    // ADC input commands

    async getInputVoltage(channel: number): Promise<number> {
        assertChannel(channel, 12);
        return parseFloat( await this.scpi.query(`INP${channel}:VOLT?`) )
    }

    // DAC output commands

    async setOutputVoltage(channel: number, volts: number) {
        assertChannel(channel, 12)
        await this.scpi.write(`OUT${channel}:VOLT ${volts.toFixed(3)}V`)
    }

    async setOutputEnable(channel: number, enable: boolean) {
        assertChannel(channel, 12)
        await this.scpi.write(`OUT${channel}:ENA ${enable?"ON":"OFF"}`)
    }

    async setOutput(channel: number, enable: boolean, volts: number = 0.0) {
        assertChannel(channel, 12)
        await this.scpi.write(`OUT${channel}:SET ${enable?"ON":"OFF"}, ${volts.toFixed(3)}V`)
    }

    // PSU output commands

    async setPsuVoltage(channel: number, volts: number) {
        assertChannel(channel, 2)
        await this.scpi.write(`POW${channel}:VOLT ${volts.toFixed(3)}V`)
    }

    async setPsuCurrent(channel: number, amps: number) {
        assertChannel(channel, 2)
        await this.scpi.write(`POW${channel}:CURR ${amps.toFixed(3)}A`)
    }

    async setPsuEnable(channel: number, enable: boolean) {
        assertChannel(channel, 2)
        await this.scpi.write(`POW${channel}:ENA ${enable?"ON":"OFF"}`)
    }

    async setPsu(channel: number, enable: boolean, volts: number, amps: number) {
        //assertChannel(channel, 2)
        //await this.scpi.write(`POW${channel}:SET ${b2s(enable)}, ${n2s(volts)}V, ${n2s(amps)}A`)
        await this.setPsuVoltage(channel, volts)
        await this.setPsuCurrent(channel, amps)
        await this.setPsuEnable(channel, enable)
    }

    async getPsuVoltage(channel: number): Promise<number> {
        assertChannel(channel, 2)
        return parseFloat(await this.scpi.query(`POW${channel}:MEAS:VOLT?`))
    }

    async getPsuCurrent(channel: number): Promise<number> {
        assertChannel(channel, 2)
        return parseFloat(await this.scpi.query(`POW${channel}:MEAS:CURR?`))
    }

    // System commands

    async getVin(): Promise<number> {
        return parseFloat(await this.scpi.query("VIN?"))
    }

    async getTemperature(): Promise<number> {
        return parseFloat(await this.scpi.query("SYST:TEMP?"))
    }

    async getReferenceVoltage(): Promise<number> {
        return parseFloat(await this.scpi.query("SYST:VREF?"))
    }

    async beep(frequency: number = 2000, seconds: number = 0.1) {
        await this.scpi.write(`SYST:BEEP ${frequency}Hz, ${seconds.toFixed(3)}s`)
    }

    // Networking commands

    async getIp(): Promise<string> {
        return this.scpi.query("SYST:NET:IPAD?")
    }

    async getMac(): Promise<string> {
        return this.scpi.query("SYST:NET:MAC?")
    }

    async getHostname(): Promise<string> {
        return this.scpi.query("SYST:NET:NAME?")
    }

    async setHostname(name: string) {
        await this.scpi.write(`SYST:NET:NAME "${name}"`)
    }

    async getAddress(): Promise<string|null> {
        const addr = await this.scpi.query("SYST:NET:NAME:RES?")
        return addr.length ? addr : null;
    }

    // Aux serial commands
    
    async openSerial(baud: number = 9600) {
        await this.scpi.write(`AUX:SER:BAUD ${baud}`)
        await this.scpi.write("AUX:SER:ENA ON")
    }

    async closeSerial() {
        await this.scpi.write("AUX:SER:ENA OFF")
    }

    async getSerialRemaining(): Promise<number> {
        return parseInt(await this.scpi.query("AUX:SER:READ?"))
    }

    async writeSerial(payload: Buffer) {
        await this.scpi.write(`AUX:SER:WRITE ${bytes2hex(payload)}`)
    }

    async setDirPin(enable: boolean, activeHigh: boolean = false) {
        var mode = !enable ? "OFF" : ( activeHigh ? "TX" : "NTX" )
        await this.scpi.write(`AUX:SER:DIR ${mode}`)
    }

    private async readSerial(count: number = 256): Promise<Buffer> {
        let payload = await this.scpi.query(`AUX:SER:READ ${count}`)
        return hex2bytes(payload)
    }

    async readSerialLine(delimiter: string = "\n", timeout: number = 0) {
        const start = Date.now();
        while (true) {
            this.serialBuffer = Buffer.concat([this.serialBuffer, await this.readSerial()]);
            const index = this.serialBuffer.indexOf(delimiter);
            if (index >= 0) {
                const line = this.serialBuffer.subarray(0, index).toString();
                this.serialBuffer = this.serialBuffer.subarray(index + Buffer.from(delimiter).length);
                return line;
            }
            if ((Date.now() - start) > timeout) {
                return null;
            }
            await delay(50);
        }
    }

    async readSerialBytes(count: number, timeout: number = 0) {
        const start = Date.now();
        while (true) {
            this.serialBuffer = Buffer.concat([this.serialBuffer, await this.readSerial()]);
            if (this.serialBuffer.length >= count) {
                const data = this.serialBuffer.subarray(0, count);
                this.serialBuffer = this.serialBuffer.subarray(count);
                return data;
            }
            if ((Date.now() - start) > timeout) {
                const data = this.serialBuffer;
                this.serialBuffer = Buffer.alloc(0);
                return data;
            }
            await delay(50);
        }
    }

    // Aux I2C commands

    async openI2c(speed: number = 100000) {
        await this.scpi.write(`AUX:IIC:SPEED ${speed}`)
        await this.scpi.write("AUX:IIC:ENA ON")
    }

    async closeI2c() {
        await this.scpi.write("AUX:IIC:ENA OFF");
    }

    async readI2c(address: number, toRead: number) {
        const result = await this.scpi.query(`AUX:IIC:READ ${address}, ${toRead}`);
        return hex2bytes(result);
    }

    async writeI2c(address: number, payload: Buffer) {
        const result = await this.scpi.query(`AUX:IIC:WRITE ${address}, ${bytes2hex(payload)}`);
        return result === "ON";
    }

    async transferI2c(address: number, payload: Buffer, toRead: number) {
        const result = await this.scpi.query(`AUX:IIC:TRAN ${address}, ${bytes2hex(payload)}, ${toRead}`);
        return hex2bytes(result);
    }

    async scanI2c(address: number) {
        const result = await this.scpi.query(`AUX:IIC:SCAN ${address}`);
        return result === "ON";
    }

    async scanAllI2c() {
        const foundDevices = [];
        for (let addr = 0; addr < 0x80; addr++) {
            if (await this.scanI2c(addr)) {
                foundDevices.push(addr);
            }
        }
        return foundDevices;
    }

    async readEeprom(count: number = 16, address: number = 0x50, offset: number = 0) {
        return await this.transferI2c(address, Buffer.from([offset]), count);
    }

    async writeEeprom(payload: Buffer, address: number = 0x50, offset: number = 0, pagesize: number = 8) {
        let index = 0;
        const end = offset + payload.length;
        while (offset < end) {
            const pageEnd = (offset & ~(pagesize - 1)) + pagesize;
            const chunk = Math.min(pageEnd, end) - offset;
            
            if (!(await this.writeI2c(address, Buffer.concat([Buffer.from([offset]), payload.subarray(index, index + chunk)])))) {
                return false;
            }
            
            offset += chunk;
            index += chunk;
            
            for (let i = 0; i < 10; i++) {
                if (await this.scanI2c(address)) {
                    break;
                }
                await delay(50);
            }
        }
        return true;
    }

    // Aux GPIO commands

    async setGpio(pin: number, state: boolean) {
        assertChannel(pin, 8)
        await this.scpi.write(`AUX:GPIO${pin}:SET ${state?"ON":"OFF"}`)
    }

    async readGpio(pin: number) {
        assertChannel(pin, 8)
        return (await this.scpi.query(`AUX:GPIO${pin}:READ?`)) === "ON"
    }

    // Aux servo commands

    async setServo(pin: number, microseconds: number = 1500) {
        assertChannel(pin, 8)
        await this.scpi.write(`AUX:GPIO${pin}:SERV:SET ON, ${microseconds.toFixed(0)}us`)
    }

    async setServoEnable(pin: number, enable: boolean) {
        assertChannel(pin, 8)
        await this.scpi.write(`AUX:GPIO${pin}:SERV:ENA ${enable?"ON":"OFF"}`)
    }

    async setServoPulse(pin: number, microseconds: number) {
        assertChannel(pin, 8)
        await this.scpi.write(`AUX:GPIO${pin}:SERV:PULS ${microseconds.toFixed(0)}us`)
    }

    async setServoAngle(pin: number, degrees: number) {
        let microseconds = ((degrees / 180.0) * 1000) + 1000
        return this.setServoPulse(pin, microseconds)
    }

    static async findUsbDevices(): Promise<string[]> {
        const results = [];
        const ports = await SerialPort.list();
        for (const port of ports) {
            // WARN: vid/pid are case sensitive
            if (port.vendorId == '16d0' && port.productId == '13fd') {
                results.push(`tty://${port.path}`);
            }
        }
        return results;
    }

}

async function delay(ms: number) {
    return new Promise(resolve => setTimeout(resolve, 50));
}

function assertChannel(channel: number, maximum: number) {
    const valid = Number.isInteger(channel) && channel > 0 && channel <= maximum;
    if (!valid) {
        throw new Error(`Channel must be integer [1..${maximum}]`)
    }
}

function bytes2hex(payload: Buffer): string {
    return payload.reduce((output, elem) => 
        (output + ('0' + elem.toString(16)).slice(-2)),
        '');
}

function hex2bytes(hex: string): Buffer {
    const count = hex.length / 2
    let bytes = Buffer.alloc(count);
    for (let i = 0; i < count; i++) {
        bytes[i] = parseInt(hex.substring(i*2, i*2 + 2), 16);
    }
    return bytes;
}

export default Nautilus