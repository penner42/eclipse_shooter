echo ">>> Script Started..."

set partialExpTime "1/1000"
set beadExpTime "1/1000"
set totalityShutterSpeeds {"1/3200" "1/1000" "1/500" "1/125" "1/30" "1/8" "1/4" "1/2"}

while {1} {
    set m [dcc get mode]
    if { $m == "M" } {
        echo "Camera in Manual mode"
        break
    } else {
        echo "Error: Camera not in Manual mode"
        after 2000
    }
}

set systemTime [clock seconds]

# Set times for totality start and end
set totalityStart [clock scan "2024-04-08 3:26:30 PM"]
set totalityEnd   [clock scan "2024-04-08 3:30:00 PM"]
# TESTING ONLY
set totalityStart [expr {$systemTime + 65}]
set totalityEnd [expr {$systemTime + 125}]


echo "Current Time: [clock format $systemTime -format {%D %H:%M:%S}]"
echo "Totality Time: [clock format $totalityStart -format {%D %H:%M:%S}]"

set timeToEclipse [expr {$totalityStart - $systemTime}]
set waitCaptures [expr {int($timeToEclipse/20)}]
set timeToNextCapture [expr { $timeToEclipse - ( 20 * $waitCaptures )}]
set nextCaptureTime [expr {$systemTime + $timeToNextCapture }]
echo "Time To Totality: T-$timeToEclipse sec "
echo "Next Capture Time: [clock format $nextCaptureTime -format {%D %H:%M:%S}]"

dcc set whitebalance "Auto"
dcc set exposurecompensation "0.0"
dcc set compressionsetting "RAW"
dcc set iso "100"
dcc set shutterspeed "1/1000"

set iso [dcc get iso]
set ss [dcc get shutterspeed]
set partialCount 1

while { $timeToEclipse > 30 } {
    set systemTime [clock seconds]
    while { $systemTime < $nextCaptureTime } {
        after 1000
        set systemTime [clock seconds]
		
		set timeToEclipse [expr {$totalityStart - $systemTime}]
		if { $timeToEclipse < 120} {
			echo "Time To Totality: T-$timeToEclipse sec "
		}
    }
	
	echo "Photo #$partialCount -- ISO: $iso, Shutter Speed: $ss"
	dcc capture

    echo "Next Capture In: 20 seconds"
}

# Bailey's beads start
echo ">>> Beginning Bailey's Beads Acquisition..."
set beadCount 0
dcc set shutterspeed $beadExpTime
set ss [dcc get shutterspeed]
while { $beadCount < 30 } {
	echo "Photo #$beadCount -- ISO: $iso, Shutter Speed: $ss"
	dcc capture
	incr beadCount
}


# Totality starts
set loopcount 0
set timeToEnd [expr {$totalityEnd - $systemTime}]

echo ">>> Beginning Totality Acquisition..."
while { $timeToEnd > 30} {
	set systemTime [clock seconds]
    incr loopcount
    foreach setss $totalityShutterSpeeds {
        dcc set shutterspeed $setss
        set ss [dcc get shutterspeed]
        echo "Photo #$loopcount -- ISO: $iso, Shutter Speed: $ss"
        dcc capture
    }
	set timeToEnd [expr {$totalityEnd - $systemTime}]
	echo "Totality Over In: T-$timeToEnd sec "
}


# Bailey's beads start
echo ">>> Beginning Bailey's Beads Acquisition..."
set beadCount 0
dcc set shutterspeed $beadExpTime
set ss [dcc get shutterspeed]
while { $beadCount < 30 } {
	echo "Photo #$beadCount -- ISO: $iso, Shutter Speed: $ss"
	dcc capture
	incr beadCount
}


# Totality ends
echo ">>> Beginning Partial Acquisition..."
dcc set shutterspeed $partialExpTime
while {1} {
	echo "Photo #$partialCount -- ISO: $iso, Shutter Speed: $ss"
	incr partialCount
	dcc capture
    echo "Next Capture In: 20 seconds"
	after 20000
}