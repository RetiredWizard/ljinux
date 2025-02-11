# ------------------------------------- #
#                Ljinux                 #
#                                       #
#         Written on a aarch64          #
#    Trap card NIHIHIHAAA ACTIVATED!    #
# ------------------------------------- #

# Process stuffs
pv = {}  # Process variable container storage
pvn = {}  # Process names list
pvd = {}  # Process control data
pid_seq = -1  # PID sequence number. No need for advanced logic here.
pid_act = []  # Active process list
# It's a stack effectively, since we are operating on one thread.


class Unset:  # None 2.0
    pass


# Backend functions
def pid_alloc(pr_name, owner, resume) -> int:
    # Allocate a pid and variable storage for that process.
    global pid_seq, pid_act
    if resume and pr_name in pvn:
        res = pvn[pr_name]
        return res
    # Fall through otherwise
    pid_seq += 1
    pv[pid_seq] = {}
    pvd[pid_seq] = {}
    pvd[pid_seq]["name"] = pr_name
    pvd[pid_seq]["preserve"] = resume  # resumable task.
    pvd[pid_seq]["owner"] = owner
    pvd[pid_seq]["status"] = 0  # 0 Active, 1 Sleep, 2 Zombie.
    pvn[pr_name] = pid_seq
    return pid_seq


def pid_free(pid) -> bool:
    # End a task and wipe it's memory, returns False when stuff was tampered with.
    res = True
    if pid in pv:
        if not pvd[pid]["preserve"]:
            pvn.pop(pvd[pid]["name"])
            pvd.pop(pid)
            pv.pop(pid)
        else:
            pvd[pid]["sleep"] = 1
    else:
        res = False
    return res


def pid_activate(pid) -> bool:
    # Add pid in list of active pids.
    if pid in pv and pid not in pid_act:
        pid_act.append(pid)
        pvd[pid]["sleep"] = 0
        return True
    else:
        return False


def pid_deactivate() -> None:
    # Removes active pid from pid list.
    pid_act.pop()


# Frontend functions
def get_pid() -> int:
    # Get current active pid
    return pid_act[-1]


def get_parent_pid() -> int:
    # Get parent pid
    return pid_act[-2]


def vr(varn, dat=Unset, pid=None):
    """
    Set / Get a variable in container storage.

    You can safely pass None to be set as a value.
    """
    res = None
    if pid is None:
        pid = get_pid()
    if dat is Unset:
        # print(f"GET [{pid}][{varn}]")
        res = pv[pid][varn]
    else:
        # print(f"SET [{pid}][{varn}] = {dat}")
        pv[pid][varn] = dat
    return res


def vra(varn, dat, pid=None) -> None:
    """
    Variable append.
    Append to a variable in container storage.

    You can safely pass None to be appended.
    """
    if pid is None:
        pid = get_pid()
    # print(f"APPEND [{pid}][{varn}] + {dat}")
    pv[pid][varn].append(dat)


def vrp(varn, dat=1, pid=None) -> None:
    """
    Variable plus.
    Add something to a variable in container storage.

    Adds 1 by default.
    """
    if pid is None:
        pid = get_pid()
    # print(f"ADD [{pid}][{varn}] + {dat}")
    pv[pid][varn] += dat


def vrm(varn, dat=1, pid=None) -> None:
    """
    Variable minus.
    Subtract something to a variable in container storage.

    Subtracts 1 by default.
    """
    if pid is None:
        pid = get_pid()
    # print(f"SUB [{pid}][{varn}] - {dat}")
    pv[pid][varn] -= dat


def vrd(varn, pid=None) -> None:
    """
    Variable delete.

    Delete a variable from container storage.
    """
    if pid is None:
        pid = get_pid()
    # print(f"DEL [{pid}][{variable_name}]")
    del pv[pid][varn]


def launch_process(pr_name, owner="Nobody", resume=False):
    # Get a pid, and activate it immediately.
    if not resume:
        pr_name_og = pr_name
        pr_name_inc = 1
        while pr_name in pvn:
            pr_name = pr_name_og + str(pr_name_inc)
            pr_name_inc += 1
    tmppid = pid_alloc(pr_name, owner=owner, resume=resume)
    pid_activate(tmppid)
    # print("Launched process:", pr_name, tmppid)


def rename_process(pr_name) -> None:
    # Rename current process to target name.
    if pr_name != pvd[get_pid()]["name"]:
        pr_name_og = pr_name
        pr_name_inc = 1
        while pr_name in pvn:
            pr_name = pr_name_og + str(pr_name_inc)
            pr_name_inc += 1
        pvn.pop(pvd[get_pid()]["name"])
        pvn[pr_name] = get_pid()
        pvd[get_pid()]["name"] = pr_name
        # print("Renamed process:", pr_name, get_pid())


def end_process() -> None:
    # End current process.
    # print("End process:", pvd[get_pid()]["name"], get_pid())
    pid_free(get_pid())
    pid_deactivate()


def clear_process_storage() -> None:
    pv.pop(get_pid())
    pv[get_pid()] = {}


# Allocate kernel task
launch_process("kernel", "root", True)  # pid will always be 0
vr("Version", "0.3.7-dev")

vr("dmesg", [])
vr("access_log", [])
vr("consoles", {})
vr("console_active", None)
vr("ndmesg", False)  # disable dmesg for ram
# run _ndmesg from the shell to properly trigger it

# Core board libs
try:
    import gc

    gc.enable()

    from sys import implementation, platform, modules, exit

    import busio
    from microcontroller import cpu
    from storage import remount, VfsFat, mount, getmount
    from os import chdir, rmdir, mkdir, sync, getcwd, listdir, remove, sync, stat
    from math import trunc
    import time

    from jcurses import jcurses
    import cptoml
    from lj_colours import lJ_Colours as colors
    from traceback import format_exception
except ImportError:
    print("FATAL: Core libraries loading failed")

    from sys import exit

    exit(1)

global console
try:
    from usb_cdc import console

    pv[0]["consoles"]["ttyUSB0"] = console
    vr("console_active", "ttyUSB0")
except ImportError:
    try:
        global virtUART
        from virtUART import virtUART

        console = virtUART()
        pv[0]["consoles"]["ttyUART0"] = console
        vr("console_active", "ttyUART0")
    except ImportError:
        from sys import exit

        exit(1)

print("[    0.00000] Core modules loaded")
pv[0]["dmesg"].append("[    0.00000] Core modules loaded")

vr("digitalio_store", {})

# Exit code holder, has to be global for everyone to be able to see it.
vr("Exit", False)
vr("Exit_code", 0)

# Hardware autodetect vars, starts assuming everything is missing
vr("sdcard_fs", False)

vr("uptimee", -time.monotonic())
# using uptimee as an offset, this way uptime + time.monotonic = 0 at this very moment and it goes + from here on out
print("[    0.00000] Timings reset")
pv[0]["dmesg"].append("[    0.00000] Timings reset")

# dmtex previous end holder
pv[0]["oend"] = "\n"  # needed to mask print

try:
    term = jcurses()  # the main curses entity, used primarily for based.shell()
    term.hold_stdout = True  # set it to buffered by default
    term.console = console
    term.nwrite(colors.reset_s_format)
    print("[    0.00000] Jcurses init complete")
    pv[0]["dmesg"].append("[    0.00000] Jcurses init complete")
except ImportError:
    print("FATAL: FAILED TO INIT JCURSES")
    exit(0)


def dmtex(
    texx: str = None, end: str = "\n", timing: bool = True, force: bool = False
) -> None:
    # Persistent offset, Print "end=" preserver

    # current time since ljinux start rounded to 5 digits
    ct = "%.5f" % (pv[0]["uptimee"] + time.monotonic())

    # used to disable the time print
    strr = "[{}{}] {}".format((11 - len(ct)) * " ", str(ct), texx) if timing else texx

    if (not term.dmtex_suppress) or force:
        term.write(strr, end=end)  # using the provided end

    """
    if the oend of the last print is a newline we add a new entry
    otherwise we go to the last one and we add it along with the old oend
    """

    if not pv[0]["ndmesg"]:
        if "\n" == pv[0]["oend"]:
            pv[0]["dmesg"].append(strr)
        elif (len(pv[0]["oend"].replace("\n", "")) > 0) and (
            "\n" in pv[0]["oend"]
        ):  # there is hanging text in old oend
            pv[0]["dmesg"][-1] += pv[0]["oend"].replace("\n", "")
            pv[0]["dmesg"].append(strr)
        else:
            pv[0]["dmesg"][-1] += pv[0]["oend"] + strr
        pv[0]["oend"] = end  # oend for next


# From now on use dmtex
dmtex("Dmesg ready")

use_compiler = False
try:
    compile("", "", "exec")

    use_compiler = True
    dmtex("Kernel compiler enabled")
except NameError:
    dmtex("Kernel compiler disabled")

try:
    from neopixel_write import neopixel_write
except ImportError:
    pass  # no big deal, this just isn't a neopixel board

# Board specific configurations
defaultoptions = {  # default configuration, in line with the manual (default value, type, allocates pin bool)
    "led": ("LED", str),
    "ledtype": ("generic", str),
    "serial_console_enabled": (True, bool),
    "usb_msc_available": (False, bool),
    "usb_hid_available": (False, bool),
    "usb_midi_available": (False, bool),
    "wifi_available": (False, bool),
    "ble_available": (False, bool),
    "blc_available": (False, bool),
    "usb_msc_enabled": (False, bool),
    "usb_hid_enabled": (False, bool),
    "usb_midi_enabled": (False, bool),
    "fs_label": ("LJINUX", str),
    "DEBUG": (False, bool),
}

# General options
dmtex("Options loaded:")
for optt in list(defaultoptions.keys()):
    optt_dt = cptoml.fetch(optt, "LJINUX")
    try:
        if isinstance(optt_dt, defaultoptions[optt][1]):
            dmtex(
                "\t"
                + colors.green_t
                + "√"
                + colors.endc
                + " "
                + optt
                + "="
                + str(optt_dt),
                timing=False,
            )
        else:
            raise KeyError
    except KeyError:
        try:
            remount("/", False)
            optt_dt = defaultoptions[optt][0]
            cptoml.put(optt, optt_dt, "LJINUX")
            dmtex(
                colors.green_t + "Updated: " + colors.endc + optt + "=" + str(optt_dt),
                timing=False,
            )
            remount("/", True)
        except RuntimeError:
            dmtex("Could not update /settings.toml, usb access is enabled.")
            term.hold_stdout = True  # set it to buffered by default
            term.flush_writes()
            exit(0)
    del optt, optt_dt

del defaultoptions
gc.collect()
gc.collect()

dmtex(f"Board memory: " + str(gc.mem_alloc() + gc.mem_free()) + " bytes")
dmtex(f"Memory free: " + str(gc.mem_free()) + " bytes")
dmtex("Basic checks done")

# sd card
try:
    import adafruit_sdcard

    dmtex("TFcard libraries loaded")
except ImportError:
    dmtex(colors.error + "Notice: " + colors.endc + "TFcard libraries loading failed")

dmtex("Imports complete")


def systemprints(mod: int, tx1: str, tx2: str = None) -> None:
    dmtex(colors.white_t + "[ " + colors.endc, timing=False, end="")

    mods = {
        1: lambda: dmtex(colors.green_t + "OK", timing=False, end=""),
        2: lambda: dmtex(colors.magenta_t + "..", timing=False, end=""),
        3: lambda: dmtex(colors.red_t + "FAILED", timing=False, end=""),
        4: lambda: dmtex(colors.red_t + "EMERG", timing=False, end=""),
        5: lambda: dmtex(colors.white_t + "SKIP", timing=False, end=""),
    }
    mods[mod]()
    dmtex(colors.white_t + " ] " + colors.endc + tx1, timing=False)
    if tx2 is not None:
        dmtex("    -> ", timing=False, end="")
        dmtex(tx2, timing=False)


dmtex("Load complete")


class ljinux:
    devices = {}
    code_cache = {}

    def deinit_consoles() -> None:
        for i in vr("consoles", pid=0).keys():
            if hasattr(pv[0]["consoles"][i], "deinit"):
                pv[0]["consoles"][i].deinit()
                pv[0]["consoles"].pop(i)
                print(f"Deinit console {i}")
                time.sleep(1.2)  # Time needed for a proper disconnection

    class api:
        def remove_ansi(text: str) -> str:
            result = ""
            i = 0
            while i < len(text):
                if text[i : i + 2] == "\033[":  # Skip
                    while i < len(text) and text[i] != "m":
                        i += 1
                    i += 1
                else:
                    result += text[i]
                    i += 1
            return result

        def getvar(var: str):
            """
            Get a ljinux user variable without mem leaks
            """
            if var in ljinux.based.user_vars.keys():
                return ljinux.based.user_vars[var]
            elif var in ljinux.based.system_vars.keys():
                return ljinux.based.system_vars[var]

        def setvar(var: str, data=None, system: bool = False) -> None:
            """
            Set a ljinux user variable without mem leaks
            No handbreak installed.
            data=None deletes
            """
            if system:
                if var in ljinux.based.system_vars.keys():
                    del ljinux.based.system_vars[var]
                if data is not None:
                    ljinux.based.system_vars.update({var: data})
            else:
                if var in ljinux.based.user_vars.keys():
                    del ljinux.based.user_vars[var]
                if data is not None:
                    ljinux.based.user_vars.update({var: data})

        def xarg(rinpt: str = None, fn: bool = False) -> dict:
            """
            Proper argument parsing for ljinux.
            Send your input stream to here and you will receive a dict in return

            The return dict contains these items:
                "w" for the words that don't belong to a specific option.
                    Example: "ls /bin", "/bin" is gonna be returned in "w"
                "hw" for the words, that were hidden due to an option.
                    Example "ls -a /bin", "/bin" is not gonna be in "w"
                    as it is a part of "o" but will be in "hw".
                "o" for all the options, with their respective values.
                    Example: "ls -a /bin", {"a": "/bin"} is gonna be in "o"
                "n" if False is passed to fn, contains the filename

            Variables automatically converted to their values.
            GPIO variables unaffected.
            """

            if rinpt is None:
                rinpt = ljinux.based.user_vars["argj"]

            inpt = rinpt.split(" ")

            options = {}
            words = []
            hidwords = []

            n = False  # in keyword
            s = False  # in string
            mw = False  # multi\ word\ string
            temp_s = None  # temporary string
            entry = None  # keyword

            r = 0 if fn else 1

            for i in range(r, len(inpt)):
                if inpt[i][0] == "$":  # variable
                    if not s:
                        inpt[i] = ljinux.api.adv_input(inpt[i][1:])
                    elif inpt[i].endswith('"'):
                        temp_s += ljinux.api.adv_input(inpt[i][:-1])
                        words.append(temp_s)
                        s = False
                    elif '"' not in inpt[i]:
                        temp_s += " " + ljinux.api.adv_input(inpt[i][1:])
                        continue
                    else:
                        temp_s += " " + ljinux.api.adv_input(
                            inpt[i][1 : inpt[i].find('"')]
                        )
                        words.append(temp_s)
                        s = False
                        inpt[i] = inpt[i][inpt[i].find('"') + 1 :]
                elif inpt[i].startswith("gp#") and (
                    inpt[i][3:] in ljinux.devices["gpiochip"][0].pins
                ):
                    if not s:
                        pin_name = inpt[i][3:]
                        if pin_name not in pv[0]["digitalio_store"]:
                            if ljinux.devices["gpiochip"][0].is_free(pin_name):
                                tmp_gpio = ljinux.devices["gpiochip"][0].input(pin_name)
                                inpt[i] = str(tmp_gpio.value)
                                tmp_gpio.deinit()
                            else:
                                term.write("Could not allocate GPIO " + pin_name)
                        else:
                            inpt[i] = str(pv[0]["digitalio_store"][pin_name].value)
                    elif inpt[i].endswith('"'):
                        temp_s += ljinux.api.adv_input(inpt[i][:-1])
                        words.append(temp_s)
                        s = False
                    elif '"' not in inpt[i]:
                        temp_s += " " + ljinux.api.adv_input(inpt[i][1:])
                        continue
                    else:
                        temp_s += " " + ljinux.api.adv_input(
                            inpt[i][1 : inpt[i].find('"')]
                        )
                        words.append(temp_s)
                        s = False
                        inpt[i] = inpt[i][inpt[i].find('"') + 1 :]
                elif inpt[i].startswith("adc#") and (
                    inpt[i][4:] in ljinux.devices["gpiochip"][0].pins
                ):
                    if not s:
                        pin_name = inpt[i][4:]
                        if pin_name not in pv[0]["digitalio_store"]:
                            if ljinux.devices["gpiochip"][0].is_free(pin_name):
                                tmp_gpio = ljinux.devices["gpiochip"][0].adc(pin_name)
                                inpt[i] = str(tmp_gpio.value)
                                tmp_gpio.deinit()
                            else:
                                term.write("Could not allocate GPIO " + pin_name)
                        else:
                            # Can read digitalio, ignore
                            inpt[i] = str(pv[0]["digitalio_store"][pin_name].value)
                    elif inpt[i].endswith('"'):
                        temp_s += ljinux.api.adv_input(inpt[i][:-1])
                        words.append(temp_s)
                        s = False
                    elif '"' not in inpt[i]:
                        temp_s += " " + ljinux.api.adv_input(inpt[i][1:])
                        continue
                    else:
                        temp_s += " " + ljinux.api.adv_input(
                            inpt[i][1 : inpt[i].find('"')]
                        )
                        words.append(temp_s)
                        s = False
                        inpt[i] = inpt[i][inpt[i].find('"') + 1 :]
                elif (not s) and (not mw) and inpt[i].startswith('"$'):
                    if inpt[i].endswith('"'):
                        inpt[i] = ljinux.api.adv_input(inpt[i][2:-1])
                    else:
                        temp_s = ljinux.api.adv_input(inpt[i][2:])
                        s = True
                        continue
                elif mw or ((not s) and inpt[i].endswith("\\") and len(inpt[i]) > 1):
                    if not mw:
                        mw = True
                        temp_s = [inpt[i][:-1]]
                        continue
                    elif inpt[i].endswith("\\") and len(inpt[i]) > 1:
                        temp_s.append(temp[i][:-1])
                        continue
                    else:
                        words.append(" ".join(temp_s + [inpt[i]]))
                        temp_s = None
                        mw = False
                        continue
                if not n:
                    if (not s) and inpt[i].startswith("-"):
                        if not len(inpt[i]) - 1:
                            words.append(inpt[i])
                            continue
                        entry = inpt[i][1 + (int(inpt[i].startswith("--"))) :]
                        n = True
                    elif (not s) and inpt[i].startswith('"'):
                        if not inpt[i].endswith('"'):
                            temp_s = inpt[i][1:]
                            s = True
                        else:
                            words.append(inpt[i][1:-1])
                    elif s:
                        if inpt[i].endswith('"'):
                            temp_s += " " + inpt[i][:-1]
                            words.append(temp_s)
                            s = False
                        else:
                            temp_s += " " + inpt[i]
                    else:
                        words.append(inpt[i])
                else:  # in keyword
                    if (not s) and inpt[i].startswith('"'):
                        if not inpt[i].endswith('"'):
                            temp_s = inpt[i][1:]
                            s = True
                        else:
                            options.update({entry: inpt[i][1:-1]})
                            hidwords.append(inpt[i][1:-1])
                            n = False
                    elif s:
                        if inpt[i].endswith('"'):
                            temp_s += " " + inpt[i][:-1]
                            options.update({entry: temp_s})
                            hidwords.append(temp_s)
                            n = False
                            s = False
                        else:
                            temp_s += " " + inpt[i]
                    elif inpt[i].startswith("-"):
                        options.update({entry: None})  # no option for the previous one
                        entry = inpt[i][1 + (int(inpt[i].startswith("--"))) :]
                        # leaving n = True
                    else:
                        options.update({entry: inpt[i]})
                        hidwords.append(inpt[i])
                        n = False
            if n:  # we have incomplete keyword
                # not gonna bother if s is True
                options.update({entry: None})

            argd = {
                "w": words if words != [""] else [],
                "hw": hidwords,
                "o": options,
            }

            if r is 1:  # add the filename
                argd.update({"n": inpt[0]})
            return argd

        class fopen(object):
            """
            Ljinux standard api file operation function.
            To be used in the place of "with open()".
            Example:
              with ljinux.api.fopen("file path here", "wb", getcwd()):
            """

            def __init__(self, fname, mod="r", ctx=None):
                self.fn = fname
                self.mod = mod

            def __enter__(self):
                # print(f"DEBUG FOPEN: {self.fn}:{self.mod}")
                try:
                    rm = False  # remount
                    fname = ljinux.api.betterpath(self.fn)
                    if "w" in self.mod or "a" in self.mod:
                        if fname in ljinux.code_cache:
                            ljinux.code_cache.pop(fname)
                        rm = True
                    if rm and not pv[0]["sdcard_fs"]:
                        remount("/", False)
                    self.file = open(fname, self.mod)
                    del fname
                    if rm and not pv[0]["sdcard_fs"]:
                        remount("/", True)
                except (RuntimeError, OSError):
                    return None
                return self.file

            def __exit__(self, typee, value, traceback):
                try:
                    self.file.flush()
                    self.file.close()

                    del self.file
                except AttributeError:
                    pass
                del self.fn, self.mod

        def isdir(dirr: str, rdir: str = None) -> int:
            """
            Checks if given item is file (returns 0) or directory (returns 1).
            Returns 2 if it doesn't exist.
            """
            res = 2

            while dirr.endswith("/") and (dirr != "/"):
                dirr = dirr[:-1]
            olddir = getcwd()
            if rdir is not None:
                chdir(ljinux.api.betterpath(rdir))
            try:
                if stat(ljinux.api.betterpath(dirr))[0] == 32768:
                    res = 0
                else:
                    res = 1
            except OSError:
                pass
            chdir(olddir)
            return res

        def betterpath(back: str = None) -> str:
            """
            Ljinux standard api path translation.
            Removes the need to account for /LjinuxRoot
            """
            res = ""
            userr = ljinux.based.system_vars["USER"].lower()
            if userr != "root":
                hd = "/LjinuxRoot/home/" + ljinux.based.system_vars["USER"].lower()
            else:
                hd = "/"
            if back is None:
                a = getcwd()
                if a.startswith(hd):
                    res = "~" + a[len(hd) :]
                elif a == "/":
                    res = "&/"
                elif a == "/LjinuxRoot":
                    res = "/"
                elif a.startswith("/LjinuxRoot"):
                    res = a[11:]
                else:
                    res = "&" + a
                if " " in res:
                    res = res.replace(" ", "\\ ")
            else:  # resolve path back to normal
                if back in ["&/", "&"]:  # board root
                    res = "/"
                elif back.startswith("&/"):
                    res = back[1:]
                elif back.startswith("/LjinuxRoot"):
                    res = back  # already good
                elif back[0] == "/":
                    # This is for absolute paths
                    res = "/LjinuxRoot"
                    if back != "/":
                        res += back
                elif back[0] == "~":
                    res = hd
                    if back != "~":
                        res += back[1:]
                else:
                    res = back
            return res

        def basepath(path=".") -> str:
            old = getcwd()
            true_root = (
                (path[0] == "&")
                or (old == "/" and path == ".")
                or (old == "/LjinuxRoot" and path == "..")
            )
            path = ljinux.api.betterpath(path)
            res = ""
            try:
                chdir(path)
                res = getcwd()
                chdir(old)
            except:
                pass
            if not true_root:
                if res.startswith("/LjinuxRoot"):
                    res = res[11:]
                    if not res:
                        res = "/"
            else:
                res = "&" + res
            return res

        def listdir(path=".") -> list:
            path = ljinux.api.basepath(path)
            res = []
            if path:
                path = ljinux.api.betterpath(path)
                if path == "/LjinuxRoot/dev":  # Device enumeration done here.
                    devs = list(ljinux.devices.keys())
                    terms = list(pv[0]["consoles"].keys())
                    devs.sort()
                    terms.sort()
                    for i in devs:
                        name = i
                        if name[-1].isdigit():
                            name += "_"
                        for j in range(len(ljinux.devices[i])):
                            res.append(
                                [
                                    name + str(j),
                                    "c",
                                    [7, 7, 7],
                                    0,
                                    time.localtime(),
                                    "root",
                                    "root",
                                ]
                            )
                    for i in terms:
                        res.append(
                            [
                                i,
                                "c",
                                [7, 7, 7],
                                0,
                                time.localtime(),
                                "root",
                                "root",
                            ]
                        )
                else:
                    tmp = listdir(path)
                    tmp.sort()
                    tmpath = path if path.startswith("/LjinuxRoot") else ("&" + path)
                    for i in tmp:
                        typ = ljinux.api.isdir(tmpath + "/" + i)
                        if typ == 1:
                            typ = "d"
                        elif typ == 0:
                            typ = "f"
                        else:
                            typ = "?"
                        stati = stat(path + "/" + i)
                        res.append(
                            [
                                i,
                                typ,
                                [7, 7, 7],
                                stati[6],
                                time.localtime(
                                    stati[9]
                                    + ljinux.based.system_vars["TIMEZONE_OFFSET"] * 3600
                                ),
                                "root",
                                "root",
                            ]
                        )
                        del stati
            else:
                raise OSError("Could not traverse directory.")
            return res

        def adv_input(whatever, _type=str):
            """
            Universal variable request
            Returns the variable's value in the specified type
            Parameters:
                whatever : The name of the variable
                _type : The type in which it should be returned
            Returns:
                The result of the variable in the type
                specified if found
                Otherwise, it returns the input
            """
            res = None
            if whatever.isdigit():
                res = int(whatever)
            elif whatever in ljinux.based.user_vars:
                res = ljinux.based.user_vars[whatever]
            elif whatever in ljinux.based.system_vars:
                res = ljinux.based.system_vars[whatever]
            elif whatever in ljinux.io.sys_getters:
                res = ljinux.io.sys_getters[whatever]()
            else:
                res = whatever
            return _type(res)

        def subscript(filen: str) -> None:
            """
            Run a file directly in an existing process.

            To be used as a child process of sorts, in order
            to further segment big files.

            Scope doesn't change.
            """
            prog = None
            with ljinux.api.fopen(filen) as f:
                if f is None:
                    raise OSError
                prog = f.read()
            del filen
            gc.collect()
            try:
                if use_compiler:
                    prog = compile(prog, "subscript", "exec")
                exec(prog)
                del prog
                gc.collect()
            except KeyboardInterrupt:
                term.hold_stdout = False
                term.write("^C")
            except Exception as err:
                ljinux.based.process_failure(err)
            gc.collect()

        def console_connected() -> bool:
            for i in pv[0]["consoles"].keys():
                if hasattr(pv[0]["consoles"][i], "connected"):
                    if pv[0]["consoles"][i].connected:
                        term.console = pv[0]["consoles"][i]
                        vr("console_active", i, pid=0)
                        return True
                else:
                    # Fallback to detect_size for console detection.
                    term.console = pv[0]["consoles"][i]
                    tmpd = term.detect_size()
                    if tmpd != False:
                        vr("console_active", i, pid=0)
                        term.console.reset_input_buffer()
                        return True
                    del tmpd
            return False

    class history:
        historyy = []
        nav = [0, 0, ""]
        sz = 50
        modified = False

        def load(filen: str) -> None:
            ljinux.history.historyy = []
            with ljinux.api.fopen(filen, "r") as historyfile:
                if historyfile is not None:
                    for line in historyfile:
                        ljinux.io.ledset(3)  # act
                        ljinux.history.historyy.append(line.strip())
                        ljinux.io.ledset(1)  # idle
                else:
                    try:
                        with ljinux.api.fopen(filen, "w") as historyfile:
                            pass
                    except RuntimeError:
                        ljinux.based.error(4, filen)
            ljinux.io.ledset(1)  # idle

        def appen(itemm: str) -> None:  # add to history, but don't save to file
            ljinux.history.modified = True
            if (
                len(ljinux.history.historyy) > 0 and itemm != ljinux.history.gett(1)
            ) or len(ljinux.history.historyy) is 0:
                if len(ljinux.history.historyy) < ljinux.history.sz:
                    ljinux.history.historyy.append(itemm)
                elif len(ljinux.history.historyy) is ljinux.history.sz:
                    ljinux.history.shift(itemm)
                else:
                    ljinux.history.historyy = ljinux.history.historyy[
                        -(ljinux.history.sz - 1) :
                    ] + [itemm]

        def shift(itemm: str) -> None:
            ljinux.history.historyy.reverse()
            ljinux.history.historyy.pop()
            ljinux.history.historyy.reverse()
            ljinux.history.historyy.append(itemm)

        def save(filen: str) -> None:
            if not ljinux.history.modified:
                return
            try:
                with ljinux.api.fopen(filen, "w") as historyfile:
                    if historyfile is None:
                        raise RuntimeError
                    for item in ljinux.history.historyy:
                        historyfile.write(item + "\n")
            except (OSError, RuntimeError):
                ljinux.based.error(7, filen)

        def clear(filen: str) -> None:
            try:
                # deletes all history, from ram and storage
                a = ljinux.api.fopen(filen, "r")
                a.close()
                with ljinux.api.fopen(filen, "w") as historyfile:
                    if historyfile is None:
                        raise RuntimeError
                    historyfile.flush()
                ljinux.history.historyy.clear()
            except (OSError, RuntimeError):
                ljinux.based.error(4, filen)

        def gett(
            whichh: str,
        ) -> str:  # get a specific history item, from loaded history
            obj = len(ljinux.history.historyy) - whichh
            if obj < 0:
                raise IndexError
            return str(ljinux.history.historyy[obj])

        def getall() -> None:  # write the whole history, numbered, line by line
            for index, item in enumerate(ljinux.history.historyy):
                term.write(f"{index + 1}: {item}")

    class io:
        # Activity led
        led_setup = False
        ledtype = None

        def ledset(state) -> None:
            """
            Set the led to a state.
            state can be int with one of the predifined states,
            or a tuple like (10, 40, 255) for a custom color
            """
            if not ljinux.io.led_setup:
                return
            ljinux.devices[ljinux.io.ledtype][0].value = state

        def getled():
            if not ljinux.io.led_setup:
                return None
            return ljinux.devices[ljinux.io.ledtype][0].value

        def get_static_file(filename: str, m: str = "rb"):
            try:
                with open(filename, m) as f:
                    b = None
                    while b is None or len(b) == 2048:
                        b = f.read(2048)
                        yield b
            except OSError:
                yield f"Error: File '{filename}' Not Found"

        sys_getters = {
            "sdcard": lambda: str(vr("sdcard_fs", pid=0)),
            "uptime": lambda: str("%.5f" % (vr("uptimee", pid=0) + time.monotonic())),
            "temperature": lambda: str("%.2f" % cpu.temperature),
            "memory": lambda: str(gc.mem_free()),
            "implementation": lambda: implementation.name,
            "implementation_version": lambda: ljinux.based.system_vars[
                "IMPLEMENTATION"
            ],
            "frequency": lambda: str(cpu.frequency),
            "voltage": lambda: str(cpu.voltage),
        }

    class based:
        silent = False
        olddir = None
        pled = False  # persistent led state for nested exec
        alias_dict = {}

        user_vars = {
            "history-file": "/home/board/.history",
            "history-size": "10",
            "return": "0",
        }

        from os import uname
        from board import board_id

        system_vars = {
            "OS": "Ljinux",
            "SHELL": "Based",
            "USER": "root",
            "SECURITY": "off",
            "INIT": "normal",
            "HOSTNAME": "ljinux",
            "TERM": "xterm-256color",
            "LANG": "en_GB.UTF-8",
            "BOARD": board_id,
            "IMPLEMENTATION": ".".join(map(str, list(implementation.version))),
            "IMPLEMENTATION_RAW": uname()[3][: uname()[3].find(" on ")],
            "IMPLEMENTATION_DATE": uname()[3][uname()[3].rfind(" ") + 1 :],
            "TIMEZONE_OFFSET": 0,
        }
        del uname, board_id

        def get_internal() -> list:
            intlist = dir(ljinux.based.command)
            intlist.remove("__module__")
            intlist.remove("__qualname__")
            intlist.remove("__dict__")
            intlist.remove("__name__")  # these cannot be iterated over
            for item in intlist:
                if item.startswith("_"):
                    intlist.remove(item)
            return intlist

        def get_bins() -> list:
            try:
                return [
                    dirr[:-4]
                    for dirr in listdir("/LjinuxRoot/bin")
                    if dirr.endswith(".lja") and not dirr.startswith(".")
                ]
            except OSError:  # Yea no root, we cope
                return []

        def error(wh=3, f=None, prefix=f"{colors.magenta_t}Based{colors.endc}") -> None:
            """
            The different errors used by the based shell.
            CODE:
                ljinux.based.error([number])
                where [number] is one of the error below
            """
            ljinux.io.ledset(5)  # error
            time.sleep(0.1)
            errs = {
                1: "Syntax Error",
                2: "Input Error",
                3: "Error",
                4: f'"{f}": No such file or directory',
                5: "Network unavailable",
                6: "Display not attached",
                7: "Filesystem unwritable, board in developer mode",
                8: "Missing files",
                9: "Missing arguments",
                10: "File exists",
                11: "Not enough system memory",
                12: "Based: Error, variable already used",
                13: f"Terminal too small, minimum size: {f}",
                14: "Is a file",
                15: "Is a directory",
                16: "Directory not empty",
                17: "Not a directory",
                18: "Not a file",
                19: "Not a device",
                20: f"Unhandled exception: {f}",
            }
            term.write(f"{prefix}: {errs[wh]}")
            ljinux.io.ledset(1)

        def process_failure(err) -> None:
            # Report a process failure properly. Pass an exception.
            namee = pvd[get_pid()]["name"]
            pid = get_pid()
            ownd = pvd[get_pid()]["owner"]
            gc.collect()
            gc.collect()
            term.hold_stdout = False
            term.write(
                f"Process {namee} Failure:\n"
                + (17 + len(namee)) * "="
                + f"\n\nProcess ID (PID): {pid}\n"
                + f"Process Name: {namee}\n"
                + f"Process Owner: {ownd}\n"
                + "\nError Details:"
            )
            erl = format_exception(err)
            for i in erl:
                term.write(i)
            term.write(
                "Please take note of the above information and report it"
                + " to your system administrator for further assistance.\n"
                + "If you plan on opening a Github issue, "
                + "please provide this information along with the program.\n"
            )
            if (  # Restore dir
                ljinux.based.olddir is not None
            ) and ljinux.based.olddir != getcwd():
                chdir(ljinux.based.olddir)
            gc.collect()
            gc.collect()

        def autorun() -> int:
            launch_process("autorun")
            ljinux.io.ledset(3)  # act

            ljinux.based.system_vars["VERSION"] = pv[0]["Version"]

            term.write(
                "\nWelcome to Ljinux wannabe kernel {}!\n\n".format(
                    ljinux.based.system_vars["VERSION"]
                ),
                end="",
            )

            # Validate root exists
            try:
                chdir("/LjinuxRoot")
                chdir("/")
            except:
                systemprints(
                    4,
                    "RootValidityCheck",
                    "Cannot continue, you are on your own.",
                )
                term.hold_stdout = False
                term.flush_writes()
                return 1  # Abandon with EMERG

            ljinux.io.ledset(1)  # idle

            vr("Exit_code", 0, 0)
            ljinux.io.ledset(3)  # act
            systemprints(2, "Boot Services")
            try:
                ljinux.based.run("runparts /boot/boot.d")
                systemprints(1, "Boot Services")
            except:
                systemprints(3, "Boot Services")
            systemprints(2, "Init script")
            try:
                ljinux.io.ledset(3)  # act
                ljinux.based.command.exec("/LjinuxRoot/boot/Init.lja")
                systemprints(1, "Init script")
            except OSError:
                systemprints(3, "Init script")
            systemprints(2, "History load")
            ljinux.history.load(ljinux.based.user_vars["history-file"])
            try:
                ljinux.history.sz = int(ljinux.based.user_vars["history-size"])
            except:
                pass
            systemprints(1, "History load")
            ljinux.io.ledset(1)  # idle
            while not pv[0]["Exit"]:
                try:
                    try:
                        ljinux.based.shell()
                    except KeyboardInterrupt:
                        pass
                except KeyboardInterrupt:
                    pass
            ljinux.deinit_consoles()
            return pv[0]["Exit_code"]

        class command:
            def exec(inpt: str) -> None:
                vr("inpt", inpt.split(" "))

                if vr("inpt")[0] == "exec":
                    vr("inpt", vr("inpt")[1:])
                try:
                    with ljinux.api.fopen(vr("inpt")[0], "r") as filee:
                        for linee in filee:
                            linee = linee.strip()
                            ljinux.based.run(linee)
                    if (
                        ljinux.based.olddir is not None
                    ) and ljinux.based.olddir != getcwd():
                        chdir(ljinux.based.olddir)
                except OSError:
                    ljinux.based.error(4, vr("inpt")[0])

            def help(inpt: str) -> None:
                term.write(
                    f"LNL {colors.magenta_t}based{colors.endc}\nThese shell commands are defined internally or are in PATH.\nType 'help' to see this list.\n{colors.green_t}"
                )

                lt = set(ljinux.based.get_bins() + ljinux.based.get_internal())
                l = []
                lenn = 0
                for i in lt:
                    if not i.startswith("_"):
                        l.append(i)
                        if len(i) > lenn:
                            lenn = len(i)
                lenn += 2
                l.sort()

                for index, tool in enumerate(l):
                    term.write(tool, end=(" " * lenn).replace(" ", "", len(tool)))
                    if index % 4 == 3:
                        term.write()
                term.write(colors.endc)

            def var(inpt: str):  # variables setter / editor
                valid = True
                inpt = inpt.split(" ")
                if inpt[0] == "var":  # check if the var is passed and trim it
                    temp = inpt
                    inpt = []
                    for i in range(len(temp) - 1):
                        inpt.append(temp[i + 1])
                try:
                    # basic checks, if any of this fails, quit
                    if not inpt[0].startswith("gp#") and (
                        inpt[0][3:] in ljinux.devices["gpiochip"][0].pins
                    ):
                        for chh in inpt[0]:
                            if not (chh.islower() or chh.isupper() or chh == "-"):
                                valid = False
                                term.write("Invalid parameters")
                                break
                    if inpt[1] != "=" or not (
                        inpt[2].startswith('"')
                        or inpt[2].isdigit()
                        or inpt[2].startswith("/")
                        or inpt[2].startswith("gp#")
                        or inpt[2].startswith("adc#")
                        or inpt[2] in vr("digitalio_store", pid=0)
                    ):
                        valid = False
                    if valid:
                        new_var = ""
                        if inpt[2].startswith('"'):
                            countt = len(inpt)
                            if inpt[2].endswith('"'):
                                new_var = str(inpt[2])[1:-1]
                            elif (countt > 3) and (inpt[countt - 1].endswith('"')):
                                new_var += str(inpt[2])[1:] + " "
                                for i in range(3, countt - 1):
                                    new_var += inpt[i] + " "
                                new_var += str(inpt[countt - 1])[:-1]
                            else:
                                ljinux.based.error(1)
                                valid = False
                        elif inpt[2].startswith("gp#"):  # gpio read
                            pin_name = inpt[2][3:]
                            if ljinux.devices["gpiochip"][0].is_free(pin_name):
                                tmp_gpio = ljinux.devices["gpiochip"][0].input(pin_name)
                                new_var += str(tmp_gpio.value)
                                tmp_gpio.deinit()
                        elif inpt[2].startswith("adc#"):  # gpio read
                            pin_name = inpt[2][4:]
                            if ljinux.devices["gpiochip"][0].is_free(pin_name):
                                tmp_gpio = ljinux.devices["gpiochip"][0].adc(pin_name)
                                new_var += str(tmp_gpio.value)
                                tmp_gpio.deinit()
                        else:
                            new_var += str(inpt[2])
                    if valid:  # now do the actual set
                        if inpt[0] in ljinux.based.system_vars:
                            if not (ljinux.based.system_vars["SECURITY"] == "on"):
                                ljinux.based.system_vars[inpt[0]] = new_var
                            else:
                                term.write(
                                    colors.error
                                    + "Cannot edit system variables, security is enabled."
                                    + colors.endc
                                )
                        elif inpt[0].startswith("gp#"):
                            pin_name = inpt[0][3:]
                            if pin_name not in pv[0]["digitalio_store"]:
                                if ljinux.devices["gpiochip"][0].is_free(pin_name):
                                    pv[0]["digitalio_store"][pin_name] = ljinux.devices[
                                        "gpiochip"
                                    ][0].output(pin_name)
                                else:
                                    term.write("GPIO " + pin_name + " not available")
                                    new_var = "a"
                                if new_var.isdigit():
                                    pv[0]["digitalio_store"][pin_name].value = int(
                                        new_var
                                    )
                                else:
                                    term.write("Value not an interger")
                        elif (
                            inpt[0] == ljinux.api.adv_input(inpt[0], str)
                            or inpt[0] in ljinux.based.user_vars
                        ):
                            ljinux.based.user_vars[inpt[0]] = new_var
                except IndexError:
                    ljinux.based.error(1)

            def unset(inpt: str) -> None:  # del variables
                inpt = inpt.split(" ")
                if len(inpt):
                    a = inpt[0]
                    if a == ljinux.api.adv_input(a, str) and (
                        a.startswith("gp#") and (a[3:] not in pv[0]["digitalio_store"])
                    ):
                        ljinux.based.error(2)
                    else:
                        if a.startswith("gp#") and (
                            a[3:] in vr("digitalio_store", pid=0)
                        ):
                            pv[0]["digitalio_store"][a[3:]].deinit()
                            del pv[0]["digitalio_store"][a[3:]]
                        elif a in ljinux.based.system_vars:
                            if not (ljinux.based.system_vars["SECURITY"] == "on"):
                                del ljinux.based.system_vars[a]
                            else:
                                term.write(
                                    colors.error
                                    + "Cannot edit system variables, security is enabled."
                                    + colors.endc
                                )
                        elif a in ljinux.based.user_vars:
                            del ljinux.based.user_vars[a]
                        else:
                            raise IndexError
                else:
                    ljinux.based.error(1)

            def history(inpt):  # history frontend
                inpt = inpt.split(" ")
                if inpt[0] == "":
                    ljinux.history.getall()
                elif inpt[0] == "clear":
                    ljinux.history.clear(ljinux.based.user_vars["history-file"])
                elif inpt[0] == "load":
                    ljinux.history.load(ljinux.based.user_vars["history-file"])
                    if "history-size" in ljinux.based.user_vars:
                        ljinux.history.sz = int(ljinux.based.user_vars["history-size"])
                elif inpt[0] == "save":
                    ljinux.history.save(ljinux.based.user_vars["history-file"])
                else:
                    term.write(f"{colors.magenta_t}Based{colors.endc}: Invalid option")

            def pexec(inpt):  # Python exec
                launch_process("pexec")
                if use_compiler:
                    inpt = compile(inpt, "pexec", "exec")
                gc.collect()
                try:
                    exec(inpt)
                except KeyboardInterrupt:
                    term.write("^C")
                    if (  # Restore dir
                        ljinux.based.olddir is not None
                    ) and ljinux.based.olddir != getcwd():
                        chdir(ljinux.based.olddir)
                except Exception as err:
                    ljinux.based.process_failure(err)
                end_process()

            def fpexec(inpt):  # Python script exec
                fpargs = []
                inpt = inpt.split(" ")
                offs = 0
                if inpt[0] == "fpexec":
                    offs += 1
                try:
                    while inpt[offs].startswith("-"):
                        fpargs += list(inpt[offs][1:])
                        offs += 1
                except IndexError:
                    ljinux.based.error(9)
                    ljinux.api.setvar("return", "1")
                    return

                prog = None
                fname = ljinux.api.betterpath(inpt[offs])
                if use_compiler and fname not in ljinux.code_cache:
                    with ljinux.api.fopen(inpt[offs]) as f:
                        if f is None:
                            raise OSError
                        prog = f.read()
                del inpt
                launch_process(fname)

                try:
                    if use_compiler:
                        if fname not in ljinux.code_cache:
                            prog = compile(prog, "fpexec", "exec")
                            if gc.mem_free() > 200_000:
                                # Only cache when we have ample ram.
                                ljinux.code_cache[fname] = prog
                            elif len(ljinux.code_cache):
                                # We should clear the cache.
                                ljinux.code_cache.clear()
                        else:
                            prog = ljinux.code_cache[fname]
                    del fname
                    if not ("t" in fpargs or "l" in fpargs):
                        del fpargs
                        gc.collect()
                        exec(prog)
                    elif "i" in fpargs:
                        del fpargs
                        gc.collect()
                        exec(prog, {}, {})
                    elif "l" in fpargs:
                        del fpargs
                        gc.collect()
                        exec(prog, locals())
                except KeyboardInterrupt:
                    term.hold_stdout = False
                    term.write("^C")
                    if (  # Restore dir
                        ljinux.based.olddir is not None
                    ) and ljinux.based.olddir != getcwd():
                        chdir(ljinux.based.olddir)
                except Exception as err:
                    ljinux.based.process_failure(err)
                gc.collect()
                end_process()

            def terminal(inpt: str) -> None:  # Manage active terminal
                opts = inpt.split(" ")
                if "--help" in opts or "-h" in opts or (not len(opts)) or opts[0] == "":
                    term.write("Usage: terminal [get/list/activate] [ttyXXXX]")
                else:
                    if opts[0] == "get":
                        term.write(globals()["console_active"])
                    elif opts[0] == "activate":
                        if len(opts) > 1 and opts[1] in pv[0]["consoles"]:
                            term.console = pv[0]["consoles"][opts[1]]
                            pv[0]["console_active"] = opts[1]
                        else:
                            term.write("Console not found.")
                    elif opts[0] == "list":
                        for i in pv[0]["consoles"].keys():
                            term.nwrite(i)
                            if i == pv[0]["console_active"]:
                                term.write(" [ACTIVE]")
                            else:
                                term.write()
                    else:
                        term.write(
                            "Unknown option specified, try running `terminal --help`"
                        )

        def parse_pipes(inpt: str):
            # This is a pipe
            p_and = "&&" in inpt
            p_to = "|" in inpt

            comlist = []
            silencelist = []
            comindex = -1

            if p_and and p_to:  # TODO
                # silencelist.append(False)
                # silencelist.append(True)
                pass
            elif p_and:
                while "&&" in inpt:
                    silencelist.append(False)
                    comlist.append(inpt[: inpt.find("&&")])
                    inpt = inpt[inpt.find("&&") + 2 :]
                    comindex += 1
                    while comlist[comindex].endswith(" "):
                        comlist[comindex] = comlist[comindex][:-1]
                    while comlist[comindex].startswith(" "):
                        comlist[comindex] = comlist[comindex][1:]

                while inpt.endswith(" "):
                    inpt = inpt[:-1]
                while inpt.startswith(" "):
                    inpt = inpt[1:]
                silencelist.append(False)
                comlist.append(inpt)
            elif p_to:  # TODO
                # silencelist.append(False)
                # silencelist.append(True)
                pass
            else:
                silencelist.append(False)
                comlist.append(inpt)

            return comlist, silencelist

        def run(executable, argv=None) -> None:
            # runs any single command

            ledmine = False  # ownership of led
            oldled = None
            if not ljinux.based.pled:
                ljinux.based.pled = True
                ljinux.io.ledset(3)
                ledmine = True
            else:
                oldled = ljinux.io.getled()
                ljinux.io.ledset(3)

            if isinstance(argv, list):
                argv = " ".join(argv)
            elif argv is None:
                splitt = executable.split(" ")
                if len(splitt) > 1:
                    executable = splitt[0]
                    argv = " ".join(splitt[1:])
                del splitt

            if executable in ljinux.based.alias_dict.keys():
                executable = ljinux.based.alias_dict[executable]
                splitt = executable.split(" ")
                if len(splitt) > 1:
                    executable = splitt[0]
                    if argv is None:
                        argv = " ".join(splitt[1:])
                    else:
                        argv += " " + " ".join(splitt[1:])
                del splitt

            bins = ljinux.based.get_bins()
            ints = ljinux.based.get_internal()
            inbins = executable in bins
            inints = executable in ints
            del bins, ints
            gc.collect()

            if (executable == "") or executable.isspace() or executable.startswith("#"):
                pass
            elif inbins:  # external commands
                bckargj = (
                    ""
                    if "argj" not in ljinux.based.user_vars
                    else ljinux.based.user_vars["argj"]
                )
                ljinux.api.setvar(
                    "argj", executable + ("" if argv is None else (" " + argv))
                )
                ljinux.based.command.exec("/LjinuxRoot/bin/" + executable + ".lja ")
                ljinux.api.setvar("argj", bckargj)
                del bckargj
            elif inints:  # internal commands
                if argv is None:
                    exec(f'ljinux.based.command.{executable}("")')
                else:
                    exec(
                        "ljinux.based.command."
                        + executable
                        + "('"
                        + argv.replace("'", "\\'")
                        + "')"
                    )
            elif argv is not None and argv.startswith("="):  # variable operation
                ljinux.based.command.var(executable + " " + argv)
            else:  # error
                term.write(
                    f"{colors.magenta_t}Based{colors.endc}: '{executable}': command not found"
                )
                ljinux.based.user_vars["return"] = "1"

            if ledmine:
                ljinux.based.pled = False
                ljinux.io.ledset(1)
            else:
                ljinux.io.ledset(oldled)

            gc.collect()

        def shell(led: bool = True, nalias: bool = False) -> int:
            # The interactive main shell

            launch_process("based", resume=True)  # Preserve shell data.
            stored_pid = get_pid()
            term.hold_stdout = False

            if not term.enabled:
                ljinux.io.ledset(4)  # waiting for serial
                term.start()
                ljinux.io.ledset(1)  # idle
                term.trigger_dict = {
                    "enter": 0,
                    "ctrlC": 1,
                    "ctrlD": 2,
                    "ctrlL": 13,
                    "tab": 3,
                    "up": 4,
                    "down": 7,
                    "pgup": 11,
                    "pgdw": 12,
                    "overflow": 14,
                    "rest": "stack",
                    "rest_a": "common",
                    "echo": "common",
                    "idle": 20,
                }

            if "trigger_dict_bck" not in pv[get_pid()].keys():  # First run
                # Backup jcurses key config in case apps modify it.
                vr("trigger_dict_bck", term.trigger_dict.copy())
                pvd[get_pid()]["preserve"] = True  # Do not wipe process storage

            if (
                "based_hist" in pv[get_pid()].keys()
                and vr("based_hist_sz") != ljinux.history.historyy
            ):
                ljinux.history.sz = vr("based_hist_sz")
                ljinux.history.historyy = vr("based_hist").copy()
            ljinux.history.nav = [0, 0, ""]

            command_input = None
            if not pv[0]["Exit"]:
                if term.trigger_dict != vr("trigger_dict_bck"):
                    # Restore jcurses key config
                    term.trigger_dict = vr("trigger_dict_bck").copy()

                while ((command_input == None) or (command_input == "\n")) and not pv[
                    0
                ]["Exit"]:
                    term.trigger_dict["prefix"] = (
                        colors.white_t
                        + "["
                        + colors.cyan_t
                        + ljinux.based.system_vars["USER"]
                        + colors.white_t
                        + "@"
                        + colors.cyan_t
                        + ljinux.based.system_vars["HOSTNAME"]
                        + colors.white_t
                        + " | "
                        + colors.yellow_t
                        + ljinux.api.betterpath()
                        + colors.white_t
                        + "]"
                        + colors.blue_t
                        + "> "
                        + colors.endc
                    )
                    if term.trigger_dict != vr("trigger_dict_bck"):
                        # Update backup
                        vr("trigger_dict_bck", term.trigger_dict.copy())
                    command_input = None
                    while (command_input in [None, ""]) and not pv[0]["Exit"]:
                        term.program()
                        if term.buf[0] is 0:  # enter
                            ljinux.history.nav[0] = 0
                            command_input = term.buf[1]
                            term.buf[1] = ""
                            term.focus = 0
                            term.write()
                        elif term.buf[0] is 1:
                            ljinux.io.ledset(2)  # keyact
                            term.write("^C")
                            term.buf[1] = ""
                            term.focus = 0
                            term.clear_line()
                            ljinux.io.ledset(1)  # idle
                        elif term.buf[0] is 2:
                            ljinux.io.ledset(2)  # keyact
                            try:
                                term.write("^D")
                            except:
                                pass
                            ljinux.based.command.fpexec("/LjinuxRoot/bin/exit.py")
                            break
                        elif term.buf[0] is 3:  # tab key
                            if len(term.buf[1]):
                                ljinux.io.ledset(2)  # keyact
                                tofind = term.buf[1]  # made into var for speed reasons
                                candidates = []
                                slicedd = tofind.split()
                                lent = len(slicedd)
                                if lent > 1:  # suggesting files
                                    files = listdir()
                                    for i in files:
                                        if i.startswith(
                                            slicedd[lent - 1]
                                        ):  # only on the arg we are in
                                            candidates.append(i)
                                else:  # suggesting bins
                                    bins = ljinux.based.get_bins()
                                    ints = ljinux.based.get_internal()
                                    for i in [ints, bins]:
                                        for j in i:
                                            if j.startswith(tofind):
                                                candidates.append(j)
                                if len(candidates) > 1:
                                    term.write()
                                    for i in candidates:
                                        if not i.startswith("_"):  # discard those
                                            term.nwrite("    " + i)
                                    del i
                                    term.focus = 0
                                    term.write()
                                elif len(candidates) == 1:
                                    term.clear_line()
                                    if lent > 1:
                                        term.buf[1] = " ".join(
                                            slicedd[:-1]
                                            + [candidates[0].replace(" ", "\\ ")]
                                        )
                                    else:
                                        term.buf[1] = candidates[0]
                                    term.focus = 0
                                else:
                                    term.clear_line()
                                ljinux.io.ledset(1)  # idle
                            else:
                                term.clear_line()
                        elif term.buf[0] is 4:  # up
                            ljinux.io.ledset(2)  # keyact
                            try:
                                neww = ljinux.history.gett(ljinux.history.nav[0] + 1)
                                # if no historyitem, we wont run the items below
                                if not ljinux.history.nav[0]:
                                    ljinux.history.nav[2] = term.buf[1]
                                    ljinux.history.nav[1] = term.focus
                                term.buf[1] = neww
                                ljinux.history.nav[0] += 1
                                term.focus = 0
                            except IndexError:
                                pass
                            term.clear_line()
                            ljinux.io.ledset(1)  # idle
                        elif term.buf[0] is 7:  # down
                            ljinux.io.ledset(2)  # keyact
                            if ljinux.history.nav[0] > 0:
                                if ljinux.history.nav[0] > 1:
                                    term.buf[1] = ljinux.history.gett(
                                        ljinux.history.nav[0] - 1
                                    )
                                    ljinux.history.nav[0] -= 1
                                    term.focus = 0
                                else:
                                    # have to give back the temporarily stored one
                                    term.buf[1] = ljinux.history.nav[2]
                                    term.focus = ljinux.history.nav[1]
                                    ljinux.history.nav[0] = 0
                            term.clear_line()
                        elif term.buf[0] in [11, 12]:  # pgup / pgdw
                            term.clear_line()
                        elif term.buf[0] is 13:  # Ctrl + L (clear screen)
                            term.clear()
                        elif term.buf[0] is 14:  # overflow
                            store = term.buf[1]
                            term.focus = 0
                            term.buf[1] = ""
                            term.trigger_dict["prefix"] = "> "
                            term.clear_line()
                            term.program()
                            if term.buf[0] is 0:  # enter
                                ljinux.history.nav[0] = 0
                                command_input = store + term.buf[1]
                                term.buf[1] = ""
                                term.write()
                            elif term.buf[0] is 14:  # more lines
                                store += term.buf[1]
                                ljinux.history.nav[0] = 0
                                term.buf[1] = ""
                                term.focus = 0
                                term.clear_line()
                            else:  # not gonna
                                term.buf[0] = ""
                                term.focus = 0
                                ljinux.history.nav[0] = 0
                        elif term.buf[0] is 20:  # console disconnected
                            if not ljinux.api.console_connected():
                                ljinux.based.run("runparts /etc/hooks/disconnect.d/")
                            ljinux.based.command.exec(
                                "/LjinuxRoot/bin/_waitforconnection.lja"
                            )

                if not pv[0]["Exit"]:
                    res = ""
                    if led:
                        ljinux.io.ledset(3)  # act
                    if not (
                        command_input == ""
                        or command_input.isspace()
                        or command_input.startswith("#")
                    ):
                        # Save to history
                        if command_input.startswith(" "):
                            while command_input.startswith(" "):
                                command_input = command_input[1:]
                        else:
                            ljinux.history.appen(command_input.strip())

                        # Backup history
                        vr("based_hist", ljinux.history.historyy.copy())
                        vr("based_hist_sz", ljinux.history.sz)

                        # Output to file
                        p_write = ">" in command_input

                        # Remove > pipe from line, TODO

                        # Fetch list of commands
                        comlist, silencelist = ljinux.based.parse_pipes(command_input)
                        if len(comlist) > 1:
                            comlist.reverse()
                            silencelist.reverse()
                        while len(comlist):
                            currentcmd = comlist.pop()
                            silencecmd = silencelist.pop()
                            if silencecmd:
                                ljinux.based.silent = True
                            try:
                                ljinux.based.run(currentcmd)
                            except KeyboardInterrupt:
                                """
                                DO NOT REMOVE.

                                Without this, it will be caught in a
                                higher-up-the-stack `except KeyboardInterrupt`.
                                """
                                term.write("^C")
                            except Exception as Err:
                                term.flush_writes()
                                ljinux.based.error(20, format_exception(Err))
                                while get_pid() != stored_pid:
                                    end_process()
                            if silencecmd:
                                ljinux.based.silent = False

                        # Write stdout to file, TODO

                        gc.collect()
                        gc.collect()
                    if led:
                        ljinux.io.ledset(1)  # idle
                    gc.collect()
                    gc.collect()
                    end_process()
                    return res
