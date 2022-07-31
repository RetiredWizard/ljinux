ljinux.io.ledset(1)  # we don't want to pretend activity
sizee = term.detect_size()
if sizee[0] > 14 and sizee[1] > 105:
    filee = None
    exists = 2
    weltxt = "[ Welcome to nano.  For basic help, type Ctrl+G. ]"

    versionn = "1.0"

    try:
        filee = ljinux.based.fn.betterpath(ljinux.based.user_vars["argj"].split()[1])
    except IndexError:
        pass

    if filee is not None:  # there is arg
        exists = ljinux.based.fn.isdir(filee, rdir=getcwd())

    if exists == 1:  # it is dir
        filee = None
        exists = 2
        weltxt = "[ {} is a directory ]".format(filee[filee.rfind("/") + 1 :])

    dataa = [""]

    lc = 0  # line count
    if exists == 0:  # is file
        with open(filee, "r") as f:
            ll = f.readlines()
            ljinux.based.user_vars["input"] = []
            for i in range(0, len(ll)):
                if ll[i] != "\n":
                    ljinux.based.user_vars["input"].append(ll[i].replace("\n", ""))
                else:
                    ljinux.based.user_vars["input"].append("")
            del ll

        ljinux.based.command.fpexecc(
            [None, "-n", "/LjinuxRoot/bin/stringproccessing/line_wrap.py"]
        )
        del ljinux.based.user_vars["input"]
        dataa = ljinux.based.user_vars["output"]
        lc = len(dataa)
        del ljinux.based.user_vars["output"]
    
    # in case of empty file
    if dataa == []:
        dataa = [""]

    term_old = term.trigger_dict
    term.trigger_dict = {
        "ctrlX": 1,
        "ctrlK": 9,
        "ctrlC": 0,
        "up": 2,
        "down": 8,
        "pgup": 4,
        "pgdw": 5,
        "enter": 10,
        "overflow": 10,
        "rest": "stack",
        "rest_a": "common",
        "echo": "common",
        "prefix": "",
    }

    target = sizee[0] - 3  # no of lines per screen
    cl = 0  # current line
    vl = 0  # 1st visible line
    ctl = [0, None]
    fnam = "New buffer" if exists == 2 else filee[filee.rfind("/") + 1 :]
    spz = int((sizee[1] - 11 - len(versionn) - len(fnam)) / 2)
    sps1 = " " * (spz - 5)
    sps2 = " " * (spz + 6)
    del spz

    toptxt = f"{colors.white_bg_black_bg}  LNL nano {versionn}{sps1}{fnam}{sps2}{colors.endc}\n"
    del versionn, sps1, sps2, fnam

    bottxt = f"{colors.white_bg_black_bg}{weltxt}{colors.endc}\n"
    bottxt_offs = int((sizee[1] - len(weltxt)) / 2)
    del weltxt

    toolsplit = " " * int(sizee[1] / 8 - 13)
    
    toolbar_items = [
        "^G",
        " Help      ",
        "^O",
        " Write Out ",
        "^W",
        " Where Is  ",
        "^K",
        " Cut       ",
        "^T",
        " Execute   ",
        "^C",
        " Location  ",
        "M-U",
        " Undo      ",
        "M-A",
        " Set Mark  ",
        "\n^X",
        " Exit      ",
        "^R",
        " Read File ",
        "^\\",
        " Replace   ",
        "^U",
        " Paste     ",
        "^J",
        " Justify   ",
        "^_",
        " Go To Line",
        "M-E",
        " Redo      ",
        "M-6",
        " Copy"
    ]

    toolbar_txt = ""

    for i in range(0, len(toolbar_items), 2):
        toolbar_txt += colors.white_bg_black_bg + toolbar_items[i] + colors.endc + toolbar_items[i+1] + toolsplit
    del toolbar_items

    q = True
    inb = False  # in bottom box
    bmod = None  # 0 == saving, 1 == searching, more planned later
    savee = 0
    term.clear()
    stdout.write(toptxt)
    del toptxt # not gonna use it again
    term.move(x=sizee[0] - 2, y=bottxt_offs)
    stdout.write(bottxt)
    del bottxt, bottxt_offs
    stdout.write(toolbar_txt)
    if len(dataa) > 1:
        sz = sizee[0] - 2
        ld = len(dataa) + 2
        ltd = sz if sz + 2 < ld - 2 else ld
        del sz, ld
        for i in range(2, ltd):
            term.move(x=i)
            stdout.write(dataa[i - 2])
    while q:
        try:
            if not savee:
                term.buf[1] = dataa[cl]
                term.move(x=cl - vl + 2, y=len(term.buf[1]))
                term.clear_line()
            ljinux.io.ledset(1)
            ctl = term.program()
            ljinux.io.ledset(3)
            if ctl[0] == 9:  # kill
                term.focus = 0
                q = False
            elif ctl[0] == 1 and not savee:  # save
                dataa[cl] = term.buf[1]
                term.buf[1] = ""
                term.focus = 0
                term.move(x=sizee[0] - 2)
                spsz = (sizee[1] - 21) * " "
                stdout.write(f"{colors.white_bg_black_bg}Save modified buffer?{spsz}\n")
                term.clear_line()
                stdout.write(f" Y{colors.endc} Yes\n")
                term.clear_line()
                stdout.write(f"{colors.white_bg_black_bg} N{colors.endc} No        {toolsplit}{colors.white_bg_black_bg}^C{colors.endc} Cancel")
                term.move(x=sizee[0] - 2, y=23)
                stdout.write(colors.white_bg_black_bg)
                del spsz
                savee += 1
                
            elif ctl[0] == 8 and not savee:  # down
                term.focus = 0
                dataa[cl] = term.buf[1]
                cl += 1
                if lc-1 <= cl:
                    dataa.append("")
                    lc += 1
                if cl - vl > sizee[0] - 5:  # we are going out of screen
                    term.clear_line()
                    vl += 1
                    for i in range(2, sizee[0] - 2):  # shift data
                        term.move(x=i)
                        term.clear_line()
                        stdout.write(dataa[vl + i - 2])

            elif ctl[0] == 2 and not savee:  # up
                term.focus = 0
                dataa[cl] = term.buf[1]
                if cl > 0:
                    cl -= 1
                    if cl - vl < 0:
                        vl -= 1
                        for i in range(2, sizee[0] - 2):  # shift data
                            term.move(x=i, y=0)
                            term.clear_line()
                            stdout.write(dataa[vl + i - 2])

            elif ctl[0] == 10:  # insert empty line (enter)
                if not savee:
                    dataa[cl] = term.buf[1]
                    dataa.append(dataa[lc-1])  # last line to new line
                    noffs = 0
                    if len(term.buf[1]) == term.focus:
                        noffs -= 1
                    else:
                        term.focus = 0
                    for i in range(lc - 1, cl+1+noffs, -1):  # all lines from the end to here
                        dataa[i] = dataa[i - 1]
                    lc += 1
                    cl += 1
                    if not noffs:
                        dataa[cl] = ""
                        term.buf[1] = ""
                    else:
                        dataa[cl-1] = ""
                    del noffs
                    # shift data
                    for i in range(2, (sizee[0] - 2) if (lc > (sizee[0] - 2)) else lc+2):
                        term.move(x=i)
                        term.clear_line()
                        stdout.write(dataa[vl + i - 2])
                elif savee == 1:
                    # the "save y/n" prompt
                    if term.buf[1] in ["n", "N"]:
                        q = False # abandon all hope (, ye who enter here)
                    elif term.buf[1] in ["y", "Y"]:
                        term.buf[1] = ""
                        term.focus = 0
                        savee += 1 # 2
                        
                        # the "choose file name" prompt
                        term.move(x=sizee[0] - 2)
                        #show the file name suggested
                        term.clear_line()
                        stdout.write("File name to write:" + (" " * (sizee[1] - 19)))
                        term.move(x=sizee[0] - 1)
                        term.clear_line()
                        term.move(x=sizee[0])
                        term.clear_line()
                        stdout.write(f"^C{colors.endc} Cancel{colors.white_bg_black_bg}")
                        ffname = ""
                        try:
                            ffname = ljinux.based.user_vars["argj"].split()[1]
                        except IndexError:
                            pass
                        term.move(x=sizee[0] - 2, y=21)
                        term.buf[1] = ffname
                        term.focus = 0
                        del ffname
                elif savee == 2:
                    try:
                        if not sdcard_fs:
                            remount("/", False)
                        with open(ljinux.based.fn.betterpath(term.buf[1]), "w") as f:
                            for i in dataa:
                                f.write(f"{i}\n")
                            f.flush()
                        if not sdcard_fs:
                            remount("/", True)
                        q = False
                    except Exception as err: # anything
                        nbottxt = f'[ Failed to save "{err}" ]'
                        term.move(x=sizee[0] - 2)
                        term.clear_line()
                        term.move(x=sizee[0] - 2, y=int((sizee[1] - len(nbottxt)) / 2))
                        stdout.write(colors.white_bg_black_bg + nbottxt + colors.endc)
                        del nbottxt
                        savee = 0
                        term.buf[1] = ""
                        term.focus = 0
                        term.move(x=sizee[0] - 1)
                        stdout.write(toolbar_txt)
                        
                    
            elif ctl[0] == 0 and savee:  # Ctrl C, abort saving
                savee = 0
                term.focus = 0
                term.move(x=sizee[0] - 2)
                stdout.write(colors.endc + (" " * sizee[1]))
                term.move(x=sizee[0] - 1)
                stdout.write(toolbar_txt)
            
            elif savee:
                # counter visual bug
                stdout.write(len(term.buf[1]) * "\010")
                
        except KeyboardInterrupt:
            pass

    del q, ctl, cl, vl, target, toolbar_txt, inb, toolsplit, filee, exists
    term.clear()
    term.buf[1] = ""
    stdout.write(colors.endc)
    term.trigger_dict = term_old

    del savee, dataa, term_old
    ljinux.based.user_vars["return"] = "0"
else:
    ljinux.based.error(13, "15x106")  # minimum size error
    ljinux.based.user_vars["return"] = "1"
