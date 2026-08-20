fn start_ok() {
    start_session();
    tick();
    stop_session();
}

fn start_ok2() {
    start_session();
    tock();
    stop_session();
}

fn start_ok3() {
    start_session();
    nock();
    stop_session();
}

fn dangling_start() {
    start_session();
    tick();
    // forgot stop_session
}

fn lock_ok() {
    lock();
    work();
    unlock();
}

fn lock_ok2() {
    lock();
    work();
    unlock();
}

fn lock_ok3() {
    lock();
    work();
    unlock();
}

fn lock_if_err() {
    let g = lock();
    if g.failed() {
        return;
    }
    work();
    unlock();
}

fn start_session() {}
fn stop_session() {}
fn tick() {}
fn tock() {}
fn nock() {}
fn lock() {}
fn unlock() {}
fn work() {}
