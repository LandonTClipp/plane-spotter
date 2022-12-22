#! /bin/sh

source env.sh

case $1 in
  'run')
    exit_trap() {
        echo "exiting"
        exit 0
    }

    trap exit_trap SIGTERM

    python3 -m plane_spotter.scripts.notify
  ;;
  'sh')
    sh
  ;;
esac