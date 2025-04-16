#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
__doc__
"""

import sys
import time
import urllib.parse
from pathlib import Path

import libtorrent as lt


def parse_magnet_link(magnet_link: str) -> tuple:
    """
    __doc__
    """
    parsed_url = urllib.parse.urlparse(magnet_link)
    query_params = urllib.parse.parse_qs(parsed_url.query)

    info_hash = query_params.get("xt", ["urn", "btih", ""])[0].split(":")[2]
    file_name = query_params.get("dn", [None])[0]

    if not file_name:
        file_name = info_hash[:10]
    file_name = urllib.parse.unquote(file_name)

    return info_hash, file_name


def magnet_to_torrent(
    magnet_link: str, saved_path: str = str(Path(__file__).parent), timeout: int = 60
) -> None:
    """
    __doc__
    """
    ses = lt.session()

    params = lt.add_torrent_params()
    params.save_path = saved_path
    params.url = magnet_link

    params.flags |= lt.torrent_flags.upload_mode

    handle = ses.add_torrent(params)

    print("正在下载元数据...")

    start_time = time.time()
    while not handle.status().has_metadata:
        if time.time() - start_time > timeout:
            print("下载元数据超时！")
            sys.exit(1)

        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(1)

    print("\n元数据下载完成")

    torrent_info = handle.torrent_file()

    if torrent_info is None:
        print("无法获取种子信息！")
        sys.exit(1)

    torrent = lt.create_torrent(torrent_info)

    torrent_filename = f"{parse_magnet_link(magnet_link)[1]}.torrent"

    with open(torrent_filename, "wb") as torrent_file:
        torrent_file.write(lt.bencode(torrent.generate()))

    print(f"种子文件已生成: {torrent_filename}")


if __name__ == "__main__":

    magnet_link = (
        "magnet:?xt=urn:btih:dbef5dea789992fc174f245e1c4df4a1ef34d1f1&dn="
        "Dark%20and%20Darker%20A5%20Installer&tr=udp%3A%2F%2F"
        "tracker.openbittorrent.com%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce"
    )
    magnet_to_torrent(magnet_link)
