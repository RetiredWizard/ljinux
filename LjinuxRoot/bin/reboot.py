rename_process("reboot")
vr("inpt", ljinux.based.user_vars["argj"].split())
pv[0]["Exit"] = True
try:
    if vr("inpt")[1] == "bootloader":
        pv[0]["Exit_code"] = 243
        if hasattr(term.console, "connected"):
            term.write(
                "Please disconnect from serial to continue..\nTo continue anyways, press Ctrl + C"
            )
            try:
                while term.console.connected:
                    time.sleep(0.2)
            except KeyboardInterrupt:
                pass
    elif vr("inpt")[1] == "safemode":
        pv[0]["Exit_code"] = 242
    elif vr("inpt")[1] == "uf2":
        pv[0]["Exit_code"] = 241
    else:
        raise IndexError
except IndexError:
    pv[0]["Exit_code"] = 245
