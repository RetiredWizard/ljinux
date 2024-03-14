rename_process("builtin display init")
from drivers.displayiotty import displayiotty

pv[0]["consoles"]["ttyDISPLAY0"] = displayiotty()
be.based.run("mknod DISPLAY")
be.devices["DISPLAY"][0] = be.devices["gpiochip"][0].pin("DISPLAY", force=True)
pv[0]["consoles"]["ttyDISPLAY0"].display = be.devices["DISPLAY"][0]
pv[0]["consoles"]["ttyDISPLAY0"].enable()
del displayiotty
