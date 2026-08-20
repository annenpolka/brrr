def should_be_skipped():
    begin_tx()
    commit_tx()
    lock()
    unlock()
