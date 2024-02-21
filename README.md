# Is there entropy down there? We don't know... yet!
This repo is the result of the collaborative work between the following people:
- Gianmarco Lusvardi
- Emiliano Maccaferri (272244@studenti.unimore.it)
- (add yourself to the list)

## Disclaimer
Please, read the `LICENSE.md` file.

## The project
The scope of the project is to find exhaustive proof about entropy extraction from the system timer of a generic ARM system (at the time of writing this document, ARM is the only architecture targeted by this project). <br>
The work has been done for the Kernel Hacking exam (Unimore) and is not complete, however, we believe it to be a good foundation for further studies.

## Theoretical review
You can find more about the topic inside the `main.pdf` file. 

## Building the kernel
The work has been conducted on a Google Coral Devboard with Linux 4.14.98. The code related to this part can be found inside the `kernel-and-more/` folder.
<br>
### Step 1: get the _actual_ kernel 
To get access to the source code, please refer to the [following guide](https://coral.googlesource.com/docs/+/refs/heads/master/GettingStarted.md).<br>
The board runs a Debian-based distro called Mendel Linux: more information can be found [here](https://coral.googlesource.com/docs/+/refs/heads/master/ReadMe.md).<br>
This repo will contain everything you need to build your own version of the Linux kernel suited for the board.<br>
The directory structure should look something like this:
```
.
├── bluez-imx
├── board
├── build
├── cache
├── docs
├── GettingStarted.md -> docs/GettingStarted.md
├── imx-atf
├── imx-board-wlan
├── imx-firmware
├── imx-gpu-viv-ko
├── imx-gst1.0-plugin
├── imx-gst-plugins-bad
├── imx-gst-plugins-base
├── imx-gst-plugins-good
├── imx-gstreamer
├── libdrm-imx
├── linux-imx
├── Makefile -> build/Makefile
├── manifest
├── mendel-testing-tools
├── out
├── packages
├── prebuilts
├── releases
├── tools
├── uboot-imx
├── wayland-protocols-imx
└── weston-imx
```

### Step 2: fix build scripts
While following the guide (in particular, when building the tree), you might encounter some problems related to some dependencies missing from the whole build pipeline. <br>
To fix these problems simply copy the `build/` contents (of this repo) inside the corresponding folder inside the board's source code repo (higlighted below).
```
.
├── bluez-imx
├── board
├── build <-- files go here!
├── cache
├── docs
├── GettingStarted.md
├── imx-atf
├── imx-board-wlan
├── imx-firmware
├── imx-gpu-viv-ko
├── imx-gst1.0-plugin
├── imx-gst-plugins-bad
├── imx-gst-plugins-base
├── imx-gst-plugins-good
├── imx-gstreamer
├── libdrm-imx
├── linux-imx
├── Makefile
├── manifest
├── mendel-testing-tools
├── out
├── packages
├── prebuilts
├── releases
├── tools
├── uboot-imx
├── wayland-protocols-imx
└── weston-imx
```

### Step 3: time to patch the kernel
Copy the contents of the `kernel-and-more/board/linux-imx/include` directory inside the corresponding one inside the board's source (`linux-imx/include`). Do the same for the `kernel-and-more/board/linux-imx/kernel` folder.
<br>
Next, apply the patch located at `kernel-and-more/board/seeds.patch` while inside the `linux-imx` folder of the board's repo.
```
cd path/to/repo/linux-imx
cp path/to/kernel-and-more/board/seeds.patch .
git apply seeds.patch
```
If this doesn't work, you can simply copy the code provided in the `kernel-and-more/board/linux-imx/init/main.c` and `kernel-and-more/board/linux-imx/arch/arm64/include/arch_timer.h` files in the corresponding ones inside the board's repo.

### Step 4: you can now compile the kernel!
Phew! You can finally compile the kernel without (hopefully) any problems, with the "entropy collection" feature enabled. To do so, you can follow the [official documentation](https://coral.googlesource.com/docs/+/refs/heads/master/GettingStarted.md).

## How do I evaluate the quality of the extracted bytes?
You can use the scripts that are documented in the `main.pdf` file.<br>
The script you will use more often is `collect-raw-noise.sh`, that actually analyses the quality of the result. This script has also an "offline mode", that evaluates the quality of the samples (20) extracted at boot time.<br>
To evaluate the quality of the samples extracted at boot time, simply run:
```
mkdir output
sudo ./collect-raw-noise.sh 1 1 1 ./output true`
``` 
## Changelog
- added this README.md (21-02-2024)

## Contacts
- Emiliano Maccaferri (272244@studenti.unimore.it) - not actively maintaining the project anymore