#!/usr/bin/python3
"""
A script that reads and writes to heap
"""

import sys


def get_heap_bounds(pid):
    """
    Retrieve the start and end addresses of the heap segment
    for a given process.

    Args:
        pid (str): Process ID.

    Returns:
        tuple: Start and end addresses of the heap as integers.
    """
    try:
        with open(f'/proc/{pid}/maps', 'r') as maps_file:
            for line in maps_file:
                if "[heap]" in line:
                    addr_range = line.split(' ')[0]
                    start_str, end_str = addr_range.split('-')
                    start_addr = int(start_str, 16)
                    end_addr = int(end_str, 16)
                    return start_addr, end_addr
        print("Error: Heap segment not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Exception in get_heap_bounds: {e}")
        sys.exit(1)


def read_heap_memory(pid, start_addr, end_addr):
    """
    Read the contents of a process's heap memory.

    Args:
        pid (str): Process ID.
        start_addr (int): Start address of the heap.
        end_addr (int): End address of the heap.

    Returns:
        bytes: Data read from the heap segment.
    """
    try:
        with open(f'/proc/{pid}/mem', 'rb') as mem_file:
            mem_file.seek(start_addr)
            return mem_file.read(end_addr - start_addr)
    except Exception as e:
        print(f"Exception in read_heap_memory: {e}")
        sys.exit(1)


def write_to_heap(pid, target_addr, data):
    """
    Write data to a specific address in the process's heap.

    Args:
        pid (str): Process ID.
        target_addr (int): Memory address to write data to.
        data (bytes): Data to be written.
    """
    try:
        with open(f'/proc/{pid}/mem', 'rb+') as mem_file:
            mem_file.seek(target_addr)
            mem_file.write(data)
    except Exception as e:
        print(f"Exception in write_to_heap: {e}")
        sys.exit(1)


def main():
    """
    Main function to locate a string in the heap of a running process
    and replace it with another string of equal or shorter length.
    """
    if len(sys.argv) != 4:
        print('Usage: read_write_heap.py <pid>\
                <search_string> <replace_string>')
        sys.exit(1)

    try:
        pid = sys.argv[1]
        search_bytes = sys.argv[2].encode()
        replacement_bytes = sys.argv[3]\
            .encode().ljust(len(search_bytes), b'\x00')

        heap_start, heap_end = get_heap_bounds(pid)
        heap_data = read_heap_memory(pid, heap_start, heap_end)

        offset = heap_data.find(search_bytes)
        if offset == -1:
            print("Error: Search string not found in heap.")
            sys.exit(1)

        write_address = heap_start + offset
        write_to_heap(pid, write_address, replacement_bytes)
    except Exception as e:
        print(f"Exception in main: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
