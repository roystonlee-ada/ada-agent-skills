#!/usr/bin/env bash
# Read-only check of the adacli install. Prints one STATE line and one NEXT line.
# Changes nothing: installing and upgrading stay with the person.

TAP_FORMULA_URL="https://raw.githubusercontent.com/AdaSupport/homebrew-tap/main/Formula/adacli.rb"

os="$(uname -s)"
arch="$(uname -m)"
echo "platform: ${os} ${arch}"

if [ "$os" != "Darwin" ] && [ "$os" != "Linux" ]; then
  echo "STATE: unsupported-platform"
  echo "NEXT: Homebrew installs adacli on macOS and Linux only. Use the Ada MCP instead (see SKILL.md, MCP route)."
  exit 0
fi

if command -v brew >/dev/null 2>&1; then
  echo "homebrew: $(brew --version | head -1)"
  have_brew=1
else
  echo "homebrew: not installed"
  have_brew=0
fi

latest="$(curl -fsSL --max-time 10 "$TAP_FORMULA_URL" 2>/dev/null | sed -n 's/^ *version "\(.*\)"/\1/p' | head -1)"
echo "latest release: ${latest:-unknown (could not reach GitHub)}"

path="$(command -v adacli 2>/dev/null)"
if [ -z "$path" ]; then
  echo "adacli: not found on PATH"
  if [ "$have_brew" = 0 ]; then
    echo "STATE: no-homebrew-no-adacli"
    echo "NEXT: Install Homebrew from https://brew.sh, then run: brew install adasupport/tap/adacli"
  else
    echo "STATE: not-installed"
    echo "NEXT: brew install adasupport/tap/adacli"
  fi
  exit 0
fi

# adacli's own --version prints the bare number, for example 0.13.0
installed="$(adacli --version 2>/dev/null | head -1 | tr -d '[:space:]')"
echo "adacli: ${path} (version ${installed:-unknown})"

via_brew=0
if [ "$have_brew" = 1 ] && brew list --versions adacli >/dev/null 2>&1; then
  via_brew=1
fi

if [ "$via_brew" = 0 ]; then
  echo "installed by: not Homebrew"
  echo "STATE: installed-outside-homebrew"
  echo "NEXT: Ask the person. Keep it, or switch to the Homebrew build with: brew install adasupport/tap/adacli (then check 'which -a adacli' for the order on PATH)."
  exit 0
fi

echo "installed by: Homebrew"
if [ -z "$latest" ] || [ -z "$installed" ]; then
  echo "STATE: version-unknown"
  echo "NEXT: Run: brew update && brew outdated adasupport/tap/adacli"
elif [ "$installed" = "$latest" ]; then
  echo "STATE: up-to-date"
  echo "NEXT: Log in with: adacli <instance> login"
else
  echo "STATE: upgrade-available (${installed} to ${latest})"
  echo "NEXT: brew update && brew upgrade adasupport/tap/adacli"
fi
