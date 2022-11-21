#!/usr/bin/env python3

import base64
import html
import pathlib
import urllib.request


def start_toms_data_onion():
    path = pathlib.Path(__file__).parent / "toms-data-onion.html"

    if not path.exists():
        request = urllib.request.Request("https://www.tomdalling.com/toms-data-onion/")
        request.add_header(
            "User-Agent",
            "toms-data-onion",
        )
        with urllib.request.urlopen(request) as r:
            body = r.read()
            with open(path, "wb") as o:
                o.write(body)

    with open(path, "r") as i:
        body = i.read()

    body = html.unescape(body)

    start = body.index("<pre>") + 5
    end = body.index("</pre>")

    with open("layer-0.txt", "w") as o:
        o.write(body[start:end])


def get_payload(path: str) -> str:
    with open(pathlib.Path(__file__).parent / path) as i:
        txt = i.read()

    start = txt.index("<~")
    end = txt.index("~>", start) + 2

    return "".join(txt[start:end].splitlines())


toms_data_onion = start_toms_data_onion()

## Layer 0/6: ASCII85

layer0 = get_payload("layer-0.txt")
decoded = base64.a85decode(layer0.encode("utf-8"), adobe=True)

with open("layer-1.txt", "wb") as o:
    o.write(decoded)

## Layer 1/6: Bitwise Operations

layer1 = get_payload("layer-1.txt")
decoded = base64.a85decode(layer1.encode("utf-8"), adobe=True)
xord = [byte ^ int("01010101", 2) for byte in decoded]
rotated = [(byte >> 1) | ((byte & 1) << 7) for byte in xord]

with open("layer-2.txt", "wb") as o:
    o.write(bytearray(rotated))

## Layer 2/6: Parity Bit

layer2 = get_payload("layer-2.txt")
decoded = base64.a85decode(layer2.encode("utf-8"), adobe=True)


def is_valid_byte(byte: int):
    parity = byte & 1
    first_seven = byte >> 1
    ones = bin(first_seven).count("1")

    if ones % 2 == 0 and parity == 0:
        return True
    elif ones % 2 != 0 and parity == 1:
        return True

    return False


valid = list(filter(is_valid_byte, decoded))
chunks = [valid[i : i + 8] for i in range(0, len(valid), 8)]

with open("layer-3.txt", "wb") as o:
    for chunk in chunks:
        result = 0
        for offset in range(len(chunk)):
            result |= (chunk[offset] >> 1) << (7 * (7 - offset))
        o.write(result.to_bytes(7, byteorder="big"))
