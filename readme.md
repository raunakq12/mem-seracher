______  ___                     ________                        ______  
___   |/  /___________ ___      __  ___/__________ ________________  /_ 
__  /|_/ /_  _ \_  __ `__ \     _____ \_  _ \  __ `/_  ___/  ___/_  __ \
_  /  / / /  __/  / / / / /     ____/ //  __/ /_/ /_  /   / /__ _  / / /
/_/  /_/  \___//_/ /_/ /_/      /____/ \___/\__,_/ /_/    \___/ /_/ /_/ 
                                                                           
                                                                                                                           

Mem Search is a multi-threaded memory dump keyword search tool designed for digital forensics and ethical hacking workflows.

---

Features

- Scan raw memory dump files for keywords or regex patterns
- Multi-threaded for fast scanning
- Context-aware output (`-c`)
- Optional ASCII-only `strings` mode (`-s`)
- Whole-word match option (`-w`)
- Color-coded results in terminal
- Optional logging to a file (`-o`)

---

Usage

```bash
python memsearch.py -f memory_dump.raw -k password token APIKEY -c 40 -i
