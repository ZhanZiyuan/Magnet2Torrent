#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Convert a magnet link to a .torrent file.
"""

import os
import platform
import sys
import time
import urllib.parse
from pathlib import Path

import libtorrent as lt


def parse_magnet_link(magnet_link: str,
                      truncation: int = 10) -> tuple:
    """
    Parse the magnet link.
    """
    parsed_url = urllib.parse.urlparse(magnet_link)
    query_params = urllib.parse.parse_qs(parsed_url.query)

    info_hash = query_params.get("xt", ["urn", "btih", ""])[0].split(":")[2]
    display_name = query_params.get("dn", [None])[0]
    file_name = (
        display_name
        if display_name is not None
        else info_hash[:truncation]
    )

    return info_hash, urllib.parse.unquote(file_name)


def magnet_to_torrent(magnet_link: str,
                      saved_path: str = str(Path(__file__).parent),
                      timeout: int | float = 120,
                      truncation: int = 10) -> None:
    """
    Convert a magnet link to a .torrent file.
    """
    ses = lt.session()

    params = lt.add_torrent_params()
    params.save_path = saved_path
    params.url = magnet_link
    params.flags |= lt.torrent_flags.upload_mode

    handle = ses.add_torrent(params)

    print("Downloading metadata...")

    start_time = time.time()
    while not handle.status().has_metadata:
        if time.time() - start_time > timeout:
            print("Metadata downloading timed out!")
            sys.exit(1)

        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(1)

    print("Metadata downloading completed.")

    torrent_info = handle.torrent_file()

    if torrent_info is None:
        print("Unable to retrieve torrent information!")
        sys.exit(1)

    torrent = lt.create_torrent(torrent_info)
    torrent_filename = (
        f"{parse_magnet_link(magnet_link)[1]}"
        ".torrent"
    )

    with open(torrent_filename, "wb") as torrent_file:
        torrent_file.write(lt.bencode(torrent.generate()))

    print(f"Torrent file has been created: {torrent_filename}")


def main() -> None:
    """
    The main function.
    """
    print(
        "A script to convert a magnet link "
        "to a .torrent file.\n"
    )

    magnet_link_input = input(
        "Please input a magnet link:\n"
    ).strip()

    while True:
        saved_path_input = input(
            "Please input the directory to store the .torrent file\n"
            f"(the default is the same directory as {Path(__file__).name}):\n"
        ).strip()
        if not saved_path_input:
            saved_path_input = str(Path(__file__).parent)
        if Path(saved_path_input).exists() and Path(saved_path_input).is_dir():
            break
        else:
            print(
                "Invalid input. Please try again. "
                "Please input a valid directory. "
            )
    Path(saved_path_input).mkdir(parents=True, exist_ok=True)

    while True:
        timeout_input = input(
            "Please input the timeout for downloading metadata\n"
            "(the default is 120 seconds):\n"
        ).strip()
        if not timeout_input:
            timeout_input = "120"
        try:
            float(timeout_input)
            break
        except ValueError:
            print(
                "Invalid input. Please try again. "
                "Please input a non-negative integer or decimal. "
            )

    magnet_to_torrent(
        magnet_link=magnet_link_input,
        saved_path=saved_path_input,
        timeout=float(timeout_input),
        truncation=10
    )

    if platform.system() == "Windows":
        os.system("pause")
    else:
        os.system(
            "/bin/bash -c 'read -s -n 1 -p \"Press any key to exit.\"'"
        )
        print()


if __name__ == "__main__":

    main()
