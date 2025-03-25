import { Socket } from 'net'

class Scpi {
    async write(command: string) {
        await this.writeBytes( Buffer.from(command + "\n") )
    }

    async read(): Promise<string> {
        return (await this.readBytes()).toString().trim()
    }

    async query(command: string): Promise<string> {
        await this.write(command)
        return await this.read()
    }

    async getIdn(): Promise<string> {
        return this.query("*IDN?")
    }

    async writeBytes(command: Buffer) {
        throw new Error("Not implemented")
    }

    async readBytes(): Promise<Buffer> {
        throw new Error("Not implemented")
    }

    async open() {
        throw new Error("Not implemented")
    }

    async close() {
        throw new Error("Not implemented")
    }
}

class SerialScpi extends Scpi {
    constructor(path: string, baud: number) {
        super();
    }
}

class UdpSocketScpi extends Scpi {
    constructor(path: string, port: number) {
        super();
    }
}

class TcpSocketScpi extends Scpi {

    buffer: Buffer;
    socket: Socket;
    address: string;
    port: number;
    timeout: number;
    listener: Function | null;

    constructor(address: string, port: number) {
        super()
        this.address = address;
        this.port = port;
        this.buffer = Buffer.alloc(0)
        this.socket = new Socket()
        this.socket.setNoDelay(true)
        this.timeout = 1000
        this.listener = null;

        this.socket.on("data", (data) => {
            this.buffer = Buffer.concat([this.buffer, data]);
            this.listener?.();
        });
    }

    async open() {
        return new Promise<void>((resolve, reject) => {
            this.socket.connect(this.port, this.address, resolve);
            this.socket.once("error", reject);
        });
    }

    async close() {
        return new Promise<void>((resolve) => {
            this.socket.end(() => {
                this.socket.destroy()
                resolve()
            });
        });
    }
    
    async writeBytes(command: Buffer): Promise<void> {
        return new Promise((resolve, reject) => {
            this.socket.write(command, (err) => {
                if (err) reject(err);
                else resolve();
            });
        });
    }

    private pollBuffer(): Buffer | null {
        const index = this.buffer.indexOf("\n");
        if (index !== -1) {
            const result = this.buffer.subarray(0, index);
            this.buffer = this.buffer.subarray(index + 1);
            return result;
        }
        return null;
    }

    async readBytes(): Promise<Buffer> {
        return new Promise((resolve, reject) => {

            // Check for data immediately
            const content = this.pollBuffer();
            if (content !== null) { resolve(content); }

            // No data. Setup a timeout
            const timeout = setTimeout(() => {
                this.listener = null;
                reject(new Error("Read timeout"));
            }, this.timeout);

            // Now wait for an event to come in.
            this.listener = () => {
                const content = this.pollBuffer();
                if (content !== null) {
                    this.listener = null;
                    clearTimeout(timeout);
                    resolve(content);
                }
            }
        });
    }
}

function fromUri(uri: string, baud: number = 9600, port: number = 5025, isTcp: boolean = false): Scpi {
    const [scheme, address] = uri.split('://');
    const [addr, args] = address.includes(':') ? address.split(':') : [address, null];

    if (scheme === 'tty') {
        if (args) { baud = parseInt(args) }
        return new SerialScpi(addr, baud);
    } else if (['tcp', 'udp', 'ip'].includes(scheme)) {
        if (scheme != 'ip') { isTcp = scheme != 'udp' }
        if (args) { port = parseInt(args) }
        if (isTcp) {
            return new TcpSocketScpi(address, port)
        }
        else {
            return new UdpSocketScpi(address, port)
        }
    }

    throw new Error('URI scheme not recognized');
}

export { Scpi, fromUri };
