#!/usr/bin/python3
"""
read_write_heap.py - Find and replace a string in the heap of a running process.
Usage: sudo python3 read_write_heap.py <pid> <search_string> <replace_string>
"""

import sys
import os


def print_usage():
    print("Usage: read_write_heap.py pid search_string replace_string")


def find_heap(pid):
    """
    Find the heap address range of a process by reading /proc/PID/maps.
    Returns: (start_address, end_address) or exits on error.
    """
    maps_file = f"/proc/{pid}/maps"

    try:
        with open(maps_file, "r") as f:
            for line in f:
                # The heap line ends with "[heap]"
                if "[heap]" in line:
                    # Format: "start-end permissions ... [heap]"
                    # Example: "555e646e0000-555e64701000 rw-p ... [heap]"
                    addr_range = line.split()[0]
                    start_str, end_str = addr_range.split("-")
                    start = int(start_str, 16)
                    end   = int(end_str,   16)
                    print(f"[*] Heap found: 0x{start:x} -> 0x{end:x}")
                    print(f"[*] Heap size : {end - start} bytes")
                    return start, end
    except PermissionError:
        print(f"[!] Error: permission denied reading /proc/{pid}/maps (try sudo)")
        sys.exit(1)
    except FileNotFoundError:
        print(f"[!] Error: PID {pid} not found. Is the process running?")
        sys.exit(1)

    print("[!] No heap segment found for this process.")
    sys.exit(1)


def read_heap(pid, start, end):
    """Read the entire heap segment and return it as bytes."""
    mem_file = f"/proc/{pid}/mem"
    heap_size = end - start

    try:
        with open(mem_file, "rb") as f:
            f.seek(start)
            data = f.read(heap_size)
        print(f"[*] Heap read: {len(data)} bytes")
        return data
    except PermissionError:
        print(f"[!] Error: permission denied reading /proc/{pid}/mem (try sudo)")
        sys.exit(1)
    except OSError as e:
        print(f"[!] Memory read error: {e}")
        sys.exit(1)


def write_heap(pid, address, data):
    """Write data to a specific address in the process heap."""
    mem_file = f"/proc/{pid}/mem"

    try:
        with open(mem_file, "rb+") as f:
            f.seek(address)
            f.write(data)
        print(f"[*] Written: {len(data)} bytes -> address 0x{address:x}")
    except PermissionError:
        print(f"[!] Error: permission denied writing /proc/{pid}/mem (try sudo)")
        sys.exit(1)
    except OSError as e:
        print(f"[!] Memory write error: {e}")
        sys.exit(1)


def main():
    # --- Argument validation ---
    if len(sys.argv) != 4:
        print_usage()
        sys.exit(1)

    try:
        pid = int(sys.argv[1])
    except ValueError:
        print("[!] Error: pid must be an integer.")
        print_usage()
        sys.exit(1)

    search_str  = sys.argv[2]
    replace_str = sys.argv[3]

    search_bytes  = search_str.encode("ascii")
    replace_bytes = replace_str.encode("ascii")

    # Replace string cannot be longer than search string (no extra heap space)
    if len(replace_bytes) > len(search_bytes):
        print(f"[!] Error: replace_string ({len(replace_bytes)} bytes) "
              f"cannot be longer than search_string ({len(search_bytes)} bytes).")
        sys.exit(1)

    print(f"[*] PID          : {pid}")
    print(f"[*] Searching for : '{search_str}'")
    print(f"[*] Replacing with: '{replace_str}'")
    print()

    # --- Locate the heap ---
    heap_start, heap_end = find_heap(pid)

    # --- Read the heap ---
    heap_data = read_heap(pid, heap_start, heap_end)

    # --- Search for the string ---
    offset = heap_data.find(search_bytes)
    if offset == -1:
        print(f"[!] '{search_str}' not found in heap.")
        sys.exit(1)

    found_addr = heap_start + offset
    print(f"[*] '{search_str}' found at address 0x{found_addr:x} "
          f"(+{offset} bytes from heap start)")

    # --- Replace (pad with null bytes to preserve original length) ---
    # Example: "Holberton"(9 bytes) -> "maroua\0\0\0"(9 bytes)
    padded = replace_bytes + b"\x00" * (len(search_bytes) - len(replace_bytes))

    write_heap(pid, found_addr, padded)

    print()
    print(f"[+] Done! '{search_str}' -> '{replace_str}' successfully replaced.")


if __name__ == "__main__":
    main()
