func connectOK() {
    connect()
    handshake()
    disconnect()
}

func connectOK2() {
    connect()
    handshake()
    disconnect()
}

func connectOK3() {
    connect()
    handshake()
    disconnect()
}

func connectLeaked() {
    connect()
    handshake()
    // forgot disconnect
}

func attachOK() {
    attach()
    run()
    detach()
}

func attachOK2() {
    attach()
    run()
    detach()
}

func attachOK3() {
    attach()
    run()
    detach()
}

func attachOnly() {
    attach()
    run()
}

func connect() {}
func disconnect() {}
func handshake() {}
func attach() {}
func detach() {}
func run() {}
