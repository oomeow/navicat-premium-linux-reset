#!/bin/bash

CURRENT_SCRIPT_DIR=$(
	cd "$(dirname "$0")" || exit 1
	pwd
)
CURRENT_DESKTOP=$(echo "${XDG_CURRENT_DESKTOP}")
CURRENT_SCRIPT_DIR_FIXED=$(echo "${CURRENT_SCRIPT_DIR}" | sed "s|$HOME|\\\$HOME|")
PROFILE_PATH="${HOME}/.profile"
SCRIPT_PATH=${CURRENT_SCRIPT_DIR}/reset_navicat.sh
# Even if the command to execute the script is added in the .profile file,
# 	the script is not executed in KDE of archLinux, so use the autostart.
KDE_AUTOSTART_DIR=$HOME/.config/autostart/

install() {
	if [[ "$CURRENT_DESKTOP" == "KDE" ]]; then
		sed "s|script_path|${SCRIPT_PATH}|g" ./template.desktop >reset_navicat.sh.desktop
		mv ./reset_navicat.sh.desktop ${KDE_AUTOSTART_DIR}
	fi
	sed -i '/\/reset_navicat.sh/d' "${PROFILE_PATH}" >/dev/null 2>&1
	echo "bash \"${SCRIPT_PATH}\"" >>"${PROFILE_PATH}"
}

uninstall() {
	if [[ "$CURRENT_DESKTOP" == "KDE" ]]; then
		rm ${KDE_AUTOSTART_DIR}/reset_navicat.sh.desktop
	fi
	sed -i '/\/reset_navicat.sh/d' "${PROFILE_PATH}" >/dev/null 2>&1
}

if [ "$#" -eq 0 ]; then
	install
elif [ "$#" -eq 1 ] && [[ "$1" == "-u" ]]; then
	uninstall
else
	echo -e "Invalid arguments. Usage: \n [-u] \t uninstall"
fi
