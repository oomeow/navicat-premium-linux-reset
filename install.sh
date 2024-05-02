#!/bin/bash

CURRENT_SCRIPT_DIR=$(
	cd "$(dirname "$0")" || exit 1
	pwd
)
CURRENT_SCRIPT_DIR_FIXED=$(echo "${CURRENT_SCRIPT_DIR}" | sed "s|$HOME|\\\$HOME|")
PROFILE_PATH="${HOME}/.profile"

install() {
	sed -i '/\/reset-navicat.sh/d' "${PROFILE_PATH}" >/dev/null 2>&1
	echo "bash \"${CURRENT_SCRIPT_DIR_FIXED}/reset-navicat.sh\"" >>"${PROFILE_PATH}"
}

uninstall() {
	sed -i '/\/reset-navicat.sh/d' "${PROFILE_PATH}" >/dev/null 2>&1
}

if [ "$#" -eq 0 ]; then
	install
elif [ "$#" -eq 1 ] && [[ "$1" == "-u" ]]; then
	uninstall
else
	echo -e "Invalid arguments. Usage: \n [-u] \t uninstall"
fi
