pv[0]["Exit_code"] = 245
pv[0]["Exit"] = True
term.nwrite("System halted, press Ctrl+C to restart.")
try:
    while True:
        ljinux.io.ledset(2)
        sleep(0.1)
        ljinux.io.ledset(0)
        sleep(9.8)
except KeyboardInterrupt:
    term.write()
