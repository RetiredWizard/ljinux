if "network" in ljinux.modules and ljinux.modules["network"].connected == True:
    # init
    global HTTPServer, HTTPResponse
    from adafruit_httpserver.server import HTTPServer
    from adafruit_httpserver.response import HTTPResponse

    server = HTTPServer(ljinux.modules["network"]._pool)

    # fetch data
    ipconf = ljinux.modules["network"].get_ipconf()
    webconf = []
    try:
        with open(ljinux.api.betterpath("/etc/njinx/njinx.conf"), "r") as f:
            from json import load

            webconf = load(f)
            del load
    except Exception as Err:
        pass
    try:
        print(
            "Now serving "
            + webconf["path"]
            + " at "
            + str(ipconf["ip"])
            + ":"
            + str(webconf["port"])
        )

        # prepare admin
        if webconf["admin"]:

            @server.route("/admin")
            def base(request):
                return HTTPResponse(
                    filename=ljinux.api.betterpath("/var/www/admin/index.html")
                )

        # post route

        exec(
            '@server.route("/post", "POST")\n'
            + "def base(request):\n"
            + " ljinux.io.ledset(3)\n"
            + ' raw = request.raw_request.decode("utf8").split()\n'
            + ' res = "OK"\n'
            + " pos = 0\n"
            + " data = None\n"
            + " from json import loads\n"
            + " while pos < len(raw):\n"
            + '  if raw[pos].startswith("{\\""):\n'
            + '   data = loads(" ".join(raw[pos:]))\n'
            + "   break\n"
            + "  else:\n"
            + "   pos += 1\n"
            + " del raw, pos, loads\n"
            + " if data is None:\n"
            + '  res = "FAIL: Invalid form."\n'
            + " else:\n"
            + '  passwd = "'
            + ljinux.api.betterpath(webconf["password"])
            + '"\n'
            + '  if not (("auth" in data) and (data["auth"] == passwd)):\n'
            + '   res = "FAIL: Authentication failure."\n'
            + "   del passwd, data\n"
            + "  else:\n"
            + '   if "operation" in data:\n'
            + '    njcommand = data["operation"]\n'
            + "    del data\n"
            + "    term.hold_stdout = True\n"
            + "    ljinux.based.run(njcommand)\n"
            + "    del njcommand\n"
            + "    term.hold_stdout = False\n"
            + "    res = term.flush_writes(to_stdout=False)\n"
            + "   else:\n"
            + '    res = "FAIL: \\"operation\\" missing."\n'
            + "    del data\n"
            + " ljinux.io.ledset(1)\n"
            + " if res is None:\n"
            + "  res = 'None\\n'\n"
            + " return HTTPResponse(body=res)"
        )

        # prepare root routing
        exec(
            '@server.route("/")\n'
            + "def base(request):\n"
            + '    return HTTPResponse(filename="'
            + ljinux.api.betterpath(webconf["path"])
            + '/index.html")'
        )

        # eternal servitude
        print("Started. Press Ctrl + C to stop.")
        ljinux.io.ledset(1)
        ljinux.based.user_vars["return"] = "0"  # admin may edit it

        server.start(
            host=str(ipconf["ip"]),
            root_path=ljinux.api.betterpath(webconf["path"]),
            port=webconf["port"],
        )
        while True:
            try:
                server.poll()
            except KeyboardInterrupt:
                break
            except Exception as err:
                print(f"Error: {err}")
    except:
        print("Error: Njinx configuration file is invalid. Abort.")
        ljinux.based.user_vars["return"] = "1"

    # cleanup
    print("Cleaning up..")
    ljinux.modules["network"].resetsock()
    del HTTPServer, HTTPResponse, server, ipconf
else:
    ljinux.based.error(5)
    ljinux.based.user_vars["return"] = "1"
