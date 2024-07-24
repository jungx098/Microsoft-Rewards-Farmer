#!/usr/bin/env sh

PATH=/usr/local/bin:$PATH

# Max Processing Time: 5000 + 15000 secs = 5.56 hours
#   MAX_DELAY_TIME: 5000 secs = 1.39 hours
#   MAX_PROCESS_TIME: 15000 secs = 4.17 hours
MAX_DELAY_TIME=5000
MAX_PROCESS_TIME=15000

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
    PYTHON=$LOCALAPPDATA/Programs/Python/Python312/python

    # Enable the Python UTF-8 Mode.
    export PYTHONUTF8=1
fi

# Random sleep duration in seconds
DURATION=$($SHUF -i 0-$MAX_DELAY_TIME -n 1)

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
echo Sleep for "$DURATION" secs.
sleep $DURATION


#==============================================================================
# Main
#==============================================================================
$PYTHON install -r requirements.txt
timeout $MAX_PROCESS_TIME $PYTHON m5farmer.py $2

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
