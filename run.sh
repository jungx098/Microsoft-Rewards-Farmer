#!/usr/bin/env sh

PATH=/usr/local/bin:$PATH

#==============================================================================
# Greeting
#==============================================================================

echo "========================================================================"
echo "For no-wait and no-headless debug, type:"
echo "./run.sh 1 -v"
echo "========================================================================"

#==============================================================================
# Preprocessing
#==============================================================================

# Platform specific commands
SHUF=""
NOSLEEP=""
PYTHON="python"

if [ "$(uname)" = "Darwin" ]; then
    # Mac OS X platform
    echo Mac OS X platform
    SHUF="/opt/local/bin/gshuf"
    NOSLEEP="pmset noidle"
    PYTHON=python3
    :
elif [ "$(expr substr $(uname -s) 1 5)" = "Linux" ]; then
    # GNU/Linux platform
    echo GNU/Linux platform
    SHUF="shuf"
    :
elif [ "$(expr substr $(uname -s) 1 10)" = "MINGW32_NT" ]; then
    # Windows NT platform
    echo Windows NT platform
    SHUF="shuf"
    unset TZ
    PYTHON=/cygdrive/c/Python311/python
    :
elif [ "$(expr substr $(uname -s) 1 9)" = "CYGWIN_NT" ]; then
    # Cygwin NT platform
    echo Cygwin NT platform
    SHUF="shuf"
    NOSLEEP="/opt/local/bin/nosleep.sh"
    unset TZ
    PYTHON=/cygdrive/c/Python311/python
fi

# Random sleep duration in seconds between 0 and 1200 (20 mins)
DURATION=$($SHUF -i 0-1200 -n 1)

if [ -n "$1" ]; then
    DURATION="$1"
fi

# Exit if network is not available
nc -zw1 google.com 443 || \
   { echo "$(basename $0) No network connection: $(date)"; exit; }

# Start time stamp
echo "$(basename $0) Start: $(date)"

# Do not go to sleep.
if [ -n "$NOSLEEP" ]; then
    sh -c "$NOSLEEP" &
    NOSLEEP_PID=$!
fi

# Obtain current working directory and script directory
OLD_PATH=$(pwd)
SCRIPT_PATH=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

# Change to script directory
cd $SCRIPT_PATH

#==============================================================================
# Update repository
#==============================================================================
git fetch
git rebase

# Run main script after random delay seconds.
sleep $DURATION

#==============================================================================
# Main
#==============================================================================
$PYTHON m5farmer.py $2

#==============================================================================
# Housekeeping
#==============================================================================

./cleanup.sh

# Change back to old working directory
cd $OLD_PATH

# Okay to go to sleep.
if [ -n "$NOSLEEP" ]; then
    kill $NOSLEEP_PID $(pgrep -P $NOSLEEP_PID)
fi

# End time stamp
echo "$(basename $0) End: $(date)"
