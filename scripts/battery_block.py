#!/usr/bin/env python3
import subprocess
import re


def py_xgetres(res: str):
    """A really shitty ad hoc implementation of xgetres, totally non-portable and probably will fail for your .Xresources
    
    Feel free to replce it with a legit exec once someone ports xgetres from aur(tm) to nix
    """
    p = subprocess.check_output(["xrdb", "-query"])  # py35 compatibility
    entry_tokens = p.decode("utf-8").split("\n")
    fuj_entries = map(lambda s: s.split(":"), entry_tokens)
    entries = filter(lambda l: len(l) == 2, fuj_entries)
    resource_map = { k.lstrip("*"): v.lstrip() for k, v in entries }
    return resource_map[res.lstrip(".")]


def main():
    p = subprocess.check_output(["acpi", "-b"])  # py35 compatibility
    batteries_info = p.decode("utf-8").strip().split("\n")
    # TODO: what if there is no battery

    # TODO: adapat for many batteries
    battery_info = batteries_info[0]

    # TODO: if the battery output doesn't match regexp
    r = re.search(r"([\w\s]+), (\d+)%", battery_info)
    status, percentage = r.group(1).strip(), int(r.group(2))

    status = enrich_status() if status == "Unknown" else status

    STATUS_TABLE = {
        "Discharging": "DIS",
        "Charging": "CHR",
        "off-line": "DIS",
        "on-line": "CHR",
    }

    # TODO: handle unsupported status
    status_indicator = STATUS_TABLE[status]

    full_text = "{}% {}".format(percentage, status_indicator)
    short_text = full_text

    color = py_xgetres(".color14")

    if status_indicator == "DIS":
        if percentage < 20:
            color = py_xgetres(".color1")
        elif percentage < 60:
            color = py_xgetres(".color13")

    print(short_text)
    print(full_text)
    print(color)

    if percentage < 5:
        exit(33)  # sets urgent flag on i3blocks


def enrich_status():
    p = subprocess.check_output(["acpi", "-a"])  # py35 compatibility
    # TODO: does this vary by battery?
    p_output = p.decode("utf-8").strip().split("\n")[0]
    r = re.search(r":\s+([\w-]+)", p_output)
    return r.group(1)

if __name__ == "__main__":
    main()

