# Package

version       = "0.1.0"
author        = "zedeus"
description   = "An alternative front-end for Twitter"
license       = "AGPL-3.0"
srcDir        = "src"
bin           = @["nitter"]


# Dependencies

requires "nim >= 1.4.8"
requires "jester >= 0.5.0"
requires "karax#c71bc92"
requires "sass#e683aa1"
requires "regex#eeefb4f"
requires "nimcrypto#a5742a9"
requires "markdown#abdbe5e"
requires "packedjson#d11d167"
requires "supersnappy#2.1.1"
requires "redpool#f880f49"
requires "https://github.com/zedeus/redis#d0a0e6f"
requires "https://github.com/disruptek/frosty#0.3.1"


# Tasks

task scss, "Generate css":
  exec "nim c --hint[Processing]:off -r tools/gencss"
