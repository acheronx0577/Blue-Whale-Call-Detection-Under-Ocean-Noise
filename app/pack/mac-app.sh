#!/bin/sh
set -eu
root="$(cd "$(dirname "$0")/.." && pwd)"
bin="$root/target/release/whale-mix"
app="$root/target/release/Whale Mix.app"
mkdir -p "$app/Contents/MacOS"
cp "$bin" "$app/Contents/MacOS/whale-mix"
cp "$root/pack/Info.plist" "$app/Contents/Info.plist"
chmod +x "$app/Contents/MacOS/whale-mix"
