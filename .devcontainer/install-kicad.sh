#!/bin/bash

set -e

echo "Installing prerequisites..."
sudo apt update > /dev/null 2>&1 && sudo apt install -y software-properties-common > /dev/null 2>&1

echo "Installing KiCad (takes a few minutes)..."
sudo add-apt-repository -y ppa:kicad/kicad-9.0-releases > /dev/null 2>&1
sudo apt update > /dev/null 2>&1
sudo apt install -y --no-install-recommends kicad kicad-symbols kicad-footprints > /dev/null 2>&1

# Link KiCad plugin to workspace path
echo "Linking KiCad plugin..."
mkdir -p "$HOME/.local/share/kicad/9.0/3rdparty/plugins"
ln -s /workspaces/Fabrication-Toolkit/plugins "$HOME/.local/share/kicad/9.0/3rdparty/plugins/com_github_bennymeg_JLC-Plugin-for-KiCad"
