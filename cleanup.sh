#!/usr/bin/env sh

USER=$(whoami)

#==============================================================================
# Housekeeping
#==============================================================================

if [ "$(uname)" = "Darwin" ]; then
    :
elif [ "$(expr substr $(uname -s) 1  5)" = "Linux"      ]; then
    :
elif [ "$(expr substr $(uname -s) 1 10)" = "MINGW32_NT" ]; then
    # Replace '+' with '\' in $USER for domain accounts.
    USER=$(echo $USER | sed 's/+/\\/g')

    # Killing all chrome processes can resolve WebDriverException errors.
    taskkill /f /fi "USERNAME eq $USER" /im chrome.exe
    taskkill /f /fi "USERNAME eq $USER" /im undetected_chromedriver.exe
elif [ "$(expr substr $(uname -s) 1  9)" = "CYGWIN_NT"  ]; then
    # Replace '+' with '\' in $USER for domain accounts.
    USER=$(echo $USER | sed 's/+/\\/g')

    # Wait if any python process (potentially Selenium) is running.
    while
       sleep 60
       COND=$(ps | grep -i "python" | grep -v grep)
       echo "$COND"
       [ -n "$COND" ]
    do :;  done

    # Killing all chrome processes can resolve WebDriverException errors.
    taskkill /f /fi "USERNAME eq $USER" /im chrome.exe
    taskkill /f /fi "USERNAME eq $USER" /im undetected_chromedriver.exe
else
    :
fi
