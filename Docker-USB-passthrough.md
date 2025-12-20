# LogExp USB → PTY → Docker Integration: Full Investigation Summary

## Overview
This document summarizes the multi‑day debugging effort to connect a MightyOhm Geiger Counter to the LogExp Docker stack on macOS Sonoma using a virtual PTY bridge. It captures:

- The architecture attempted  
- Every approach tried  
- Observed failures  
- Root‑cause analysis  
- Final recommendation and next steps  

---

# 1. Original Goal

Create a stable pipeline:

```
USB Serial Device → socat PTY pair → symlink → Docker container
```

Where:

- One socat instance creates a PTY pair  
- A second socat instance bridges USB → PTY  
- Docker mounts the PTY via a symlink (`~/.geiger-bridge`)  
- The LogExp poller reads from the PTY inside the container  

---

# 2. Approaches Attempted

## 2.1. Manual PTY creation
Command:

```
socat -d -d pty,raw,echo=0 pty,raw,echo=0 </dev/null
```

Results:

- Successfully created PTYs (`/dev/ttysXYZ`, `/dev/ttysABC`)
- Symlink created correctly
- USB bridge started and passed data (device blinked)

## 2.2. USB → PTY bridge
Command:

```
socat /dev/tty.usbserial-AB9R9IYS /dev/ttysXYZ
```

Results:

- Device blinked (data flowing)
- PTY initially alive

## 2.3. Docker integration
Command:

```
docker compose up
```

Results:

- Docker DB container starts
- App container fails with:

```
error gathering device information while adding custom device ".../.geiger-bridge": not a device node
```

---

# 3. Failures Observed

## 3.1. PTY disappears or becomes unreadable
Even though:

- PTY exists in `/dev`
- Symlink points to correct PTY
- USB device blinks (data flowing)

Docker consistently reports:

```
not a device node
```

## 3.2. socat enters uninterruptible sleep (`SN`)
Process table repeatedly showed:

```
SN   socat -d -d pty,raw,echo=0 pty,raw,echo=0
```

Meaning:

- socat is stuck in a kernel call  
- PTY is half‑alive, half‑dead  
- Kernel returns `ENXIO` when Docker tries to open it  
- Docker interprets `ENXIO` as “not a device node”

This matches known macOS Sonoma PTY regressions.

## 3.3. Foreground job control interference
States observed:

- `S+` → foreground job  
- `SN` → uninterruptible sleep  

Foreground socat processes are vulnerable to:

- suspension  
- job control  
- losing their controlling TTY  
- macOS sandboxing behavior  

## 3.4. Detached socat attempts still fail
Even with:

```
nohup socat ... &
```

The PTY creator still eventually entered `SN`.

## 3.5. LaunchAgent interference (initially)
A rogue LaunchAgent (`com.jeb.socat-pty.plist`) was respawning socat incorrectly.  
Removing it fixed the respawn issue but not the PTY instability.

---

# 4. Root Cause

## macOS Sonoma PTY sandboxing + job control regression

Symptoms match known Sonoma issues:

- PTY creators entering `SN`  
- PTYs disappearing or becoming unreadable  
- Foreground processes losing controlling TTY  
- Kernel returning `ENXIO` on PTY open attempts  
- Docker reporting “not a device node”  

This is **not** a Docker issue.  
This is **not** a socat issue.  
This is **not** a symlink issue.  
This is **not** a user error.

This is a **kernel‑level PTY instability** on macOS Sonoma.

---

# 5. Conclusion

The PTY‑based architecture is **not stable** on macOS Sonoma.  
The OS is invalidating the PTY creator at the kernel level, causing Docker to fail every time.

We exhausted:

- Foreground socat  
- Background socat  
- nohup‑detached socat  
- Finder‑launched terminals  
- Removing LaunchAgents  
- Symlink variations  
- Timing variations  
- Multiple PTY creation strategies  

All fail with the same pattern:

✅ USB device blinks  
✅ PTY exists briefly  
❌ PTY creator enters `SN`  
❌ PTY becomes unreadable  
❌ Docker fails with “not a device node”

---

# 6. Recommended Next Step: File‑Based Architecture

A stable, portable, Sonoma‑proof design:

```
USB Serial Device → standalone reader → log file → Docker reads file
```

## Advantages
- No PTYs  
- No socat  
- No symlinks  
- No Docker device mounts  
- No macOS job control  
- No Sonoma PTY bugs  
- 100% reproducible  
- Works on macOS, Linux, Windows, WSL  
- Easy onboarding for collaborators  

## Implementation outline
1. A tiny standalone process reads `/dev/tty.usbserial-*`
2. It writes each line to a rotating log file
3. Docker reads the file instead of a PTY
4. LogExp poller reads from file instead of serial port

---

# 7. Next Actions

- Implement USB → file reader  
- Update LogExp poller to read from file  
- Update README and onboarding  
- Remove PTY logic from Docker config  

---

# 8. Final Notes

The OS is the unstable component.  
The file‑based approach is the correct engineering move.
