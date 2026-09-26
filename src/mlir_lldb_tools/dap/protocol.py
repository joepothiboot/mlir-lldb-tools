import json, threading

class Disconnect(Exception): pass

class Wire:
    def __init__(self, rfile, wfile):
        self.r, self.w = rfile, wfile
        self._seq = 0
        self._lock = threading.Lock()

    def read(self):
        length = None
        while True:
            line = self.r.readline()
            if not line: raise Disconnect()
            line = line.strip()
            if not line: break
            k, _, v = line.decode("ascii").partition(":")
            if k.strip().lower() == "content-length": length = int(v.strip())
        body = self.r.read(length)
        return json.loads(body.decode("utf-8"))

    def _write(self, msg):
        with self._lock:
            self._seq += 1; msg["seq"] = self._seq
            data = json.dumps(msg).encode("utf-8")
            self.w.write(b"Content-Length: %d\r\n\r\n" % len(data))
            self.w.write(data); self.w.flush()

    def respond(self, request, body=None, success=True, message=None):
        self._write({"type": "response", "request_seq": request["seq"],
                     "success": success, "command": request["command"],
                     **({"message": message} if message else {}),
                     "body": body or {}})

    def event(self, name, body=None):
        self._write({"type": "event", "event": name, "body": body or {}})