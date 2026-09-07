# Security Testing Commands & Components Overview

## 1. Network Discovery & Port Scanning

### `nmap`
A powerful network exploration and security auditing tool.
*   **`sudo`**: Executes the command with root/administrator privileges (required for certain raw packet scans like SYN scans).
*   **`-sS`**: TCP SYN-Scan ("Half-Open Scan"). Sends a SYN packet and waits for a response without fully establishing the connection. It is fast and stealthy.
*   **`-sV`**: Version detection. Probes open ports to determine the service and its version.
*   **`-p-`**: Scans all 65,535 TCP ports (instead of just the top 1,000).
*   **`-T3`**: Timing template. Sets the scanning speed to "Normal" (balances speed and reliability).
*   **`-oA <basename>`**: Outputs the scan results in all three major formats (Normal, XML, and Grepable) simultaneously.
*   **`-sU`**: UDP scan. Checks for open UDP ports.
*   **`--top-ports 200`**: Restricts the scan to the 200 most common ports to save time.

## 2. Web Application & HTTP Interactions

### `curl`
A command-line tool for transferring data with URLs.
*   **`-s` / `--silent`**: Silent mode. Mutes the progress bar and error messages.
*   **`-X POST`**: Specifies the HTTP method to use (POST instead of the default GET).
*   **`-d '...'`**: Data payload. Sends the specified data in the body of a POST request.
*   **`-w "%{http_code}\n"`**: Write-out format. Extracts and prints only the HTTP status code (e.g., 200, 401, 403) after the request completes.
*   **`--max-time 5`**: Sets a timeout. The operation will abort if it takes longer than 5 seconds.

### `nikto`
An open-source web server scanner that detects outdated software and common misconfigurations.
*   **`-h <URL>`**: Specifies the target host or URL.
*   **`-output <file>`**: Defines the output file name.
*   **`-Format html`**: Formats the output report as an HTML file.

### `sslscan`
A tool that queries web services to determine the SSL/TLS ciphers they support.
*   **`--show-certificate`**: Extracts and displays the full SSL/TLS certificate provided by the server.

### `zaproxy` (OWASP ZAP)
An integrated penetration testing tool for finding vulnerabilities in web applications.
*   **`-daemon`**: Runs ZAP in the background without launching the graphical user interface.
*   **`-host 127.0.0.1 -port 8090`**: Binds the ZAP proxy/API to the local loopback address on port 8090.
*   **`-config api.disablekey=true`**: Disables the API key requirement, making it easier to trigger scans via scripts (like the subsequent `curl` command).

## 3. Network Stress Testing & Flooding

### `siege`
An HTTP load testing and benchmarking utility.
*   **`-c 100`**: Concurrency. Simulates 100 simultaneous users/connections.
*   **`-t 10M`**: Time limit. Runs the test continuously for 10 minutes.
*   **`-v`**: Verbose output. Prints details of every HTTP transaction.
*   **`-l <file>`**: Logs the final transaction statistics to the specified file.

### `hping3`
A network tool able to send custom TCP/IP packets, often used for firewall testing and DoS simulations.
*   **`--flood`**: Sends packets as fast as possible without waiting for replies.
*   **`--rand-source`**: Spoofs the source IP address using random IPs to evade simple tracking/filtering.

### `macof`
A tool (part of the dsniff suite) that floods the local network with random MAC addresses. Used to test switch MAC table overflow vulnerabilities (Layer 2 DoS).
*   **`-i eth1`**: Specifies the network interface to use.

## 4. Packet Capture & Traffic Analysis

### `tcpdump`
A command-line packet analyzer.
*   **`-i eth1`**: Listens for traffic on the specified network interface (`eth1`).
*   **`host <IP>`**: BPf filter to only capture traffic going to or coming from the specified IP address.
*   **`port 80`**: BPF filter to only capture traffic on port 80 (HTTP).
*   **`-w <file>`**: Writes the captured raw packets to a `.pcap` file for later analysis in tools like Wireshark.

## 5. PROFINET & Specialized Scripts

### `python3 -c`
Executes Python code directly from the command line.
*   **`import pnio_dcp; c = pnio_dcp.DCP('eth1')`**: Initializes a PROFINET Discovery and Basic Configuration Protocol (DCP) connection on the `eth1` interface.
*   **`identify_all()`**: Broadcasts a request to find all PROFINET devices on the local network segment.
*   **`set_name_of_station(...)`**: Sends a DCP command to change the PROFINET name of the target device.
*   **`reset_to_factory(...)`**: Sends a DCP command to perform a factory reset on the target device.

## 6. Standard Linux/Bash Utilities

*   **`export SRIO=...`**: Sets an environment variable that can be referenced later in the script using `$SRIO`.
*   **`tee <file>`**: Reads standard input and writes it to both the terminal screen and a file simultaneously.
*   **`diff <file1> <file2>`**: Compares two files line by line and outputs the differences.
*   **`&` (Ampersand)**: Placed at the end of a command, it runs that command in the background, allowing the script to continue to the next line immediately.
*   **`jobs`**: Lists all active background jobs running in the current terminal session.
*   **`kill %1`**: Terminates a specific background job (in this case, job number 1).
*   **`time <command>`**: Measures and displays how long it takes for the specified command to execute.
*   **`sleep <seconds>`**: Pauses the script execution for the specified number of seconds.
*   **`(exec 3<>/dev/tcp/$SRIO/80; ... )`**: This is an advanced Bash built-in feature. It opens a raw TCP socket connection to the target IP and port and assigns it to file descriptor `3`.
*   **`printf 'GET ...' >&3`**: Sends a raw HTTP GET request directly into the opened TCP socket (`>&3`). This is used here to deliberately open a connection and hold it open without sending further data, simulating a slow-loris/connection-hold DoS attack.