#!/usr/bin/env python3
"""
read_write_heap.py - işləyən prosesin heap-indəki stringi tap və əvəz et
İstifadə: sudo python3 read_write_heap.py <pid> <search_string> <replace_string>
"""

import sys
import os


def print_usage():
    print("İstifadə: read_write_heap.py pid search_string replace_string")


def find_heap(pid):
    """
    /proc/PID/maps faylından heap-in ünvan diapazonunu tap.
    Qaytarır: (başlanğıc_ünvan, son_ünvan) və ya None
    """
    maps_file = f"/proc/{pid}/maps"

    try:
        with open(maps_file, "r") as f:
            for line in f:
                # Heap sətri "[heap]" ilə bitir
                if "[heap]" in line:
                    # Format: "başlanğıc-son permissiyalar ... [heap]"
                    # Misal: "555e646e0000-555e64701000 rw-p ... [heap]"
                    addr_range = line.split()[0]
                    start_str, end_str = addr_range.split("-")
                    start = int(start_str, 16)
                    end   = int(end_str,   16)
                    print(f"[*] Heap tapıldı: 0x{start:x} → 0x{end:x}")
                    print(f"[*] Heap ölçüsü : {end - start} bayt")
                    return start, end
    except PermissionError:
        print(f"[!] Xəta: /proc/{pid}/maps oxumaq üçün icazə lazımdır (sudo?)")
        sys.exit(1)
    except FileNotFoundError:
        print(f"[!] Xəta: PID {pid} tapılmadı. Proses işləyirmi?")
        sys.exit(1)

    print("[!] Heap tapılmadı bu prosesdə.")
    sys.exit(1)


def read_heap(pid, start, end):
    """Heap sahəsini tam oxu, bytes qaytarır."""
    mem_file = f"/proc/{pid}/mem"
    heap_size = end - start

    try:
        with open(mem_file, "rb") as f:
            f.seek(start)
            data = f.read(heap_size)
        print(f"[*] Heap oxundu: {len(data)} bayt")
        return data
    except PermissionError:
        print(f"[!] Xəta: /proc/{pid}/mem oxumaq üçün icazə lazımdır (sudo?)")
        sys.exit(1)
    except OSError as e:
        print(f"[!] Yaddaş oxuma xətası: {e}")
        sys.exit(1)


def write_heap(pid, address, data):
    """Heap-dəki müəyyən ünvana yeni data yaz."""
    mem_file = f"/proc/{pid}/mem"

    try:
        with open(mem_file, "rb+") as f:
            f.seek(address)
            f.write(data)
        print(f"[*] Yazıldı: {len(data)} bayt → ünvan 0x{address:x}")
    except PermissionError:
        print(f"[!] Xəta: /proc/{pid}/mem yazmaq üçün icazə lazımdır (sudo?)")
        sys.exit(1)
    except OSError as e:
        print(f"[!] Yaddaş yazma xətası: {e}")
        sys.exit(1)


def main():
    # --- Argument yoxlaması ---
    if len(sys.argv) != 4:
        print_usage()
        sys.exit(1)

    try:
        pid = int(sys.argv[1])
    except ValueError:
        print("[!] Xəta: pid tam ədəd olmalıdır.")
        print_usage()
        sys.exit(1)

    search_str  = sys.argv[2]
    replace_str = sys.argv[3]

    search_bytes  = search_str.encode("ascii")
    replace_bytes = replace_str.encode("ascii")

    # Replace string daha uzun ola bilməz (heap-də yer yoxdur)
    if len(replace_bytes) > len(search_bytes):
        print(f"[!] Xəta: replace_string ({len(replace_bytes)} bayt) "
              f"search_string-dən ({len(search_bytes)} bayt) uzun ola bilməz.")
        sys.exit(1)

    print(f"[*] PID         : {pid}")
    print(f"[*] Axtarılan   : '{search_str}'")
    print(f"[*] Əvəz edilən : '{replace_str}'")
    print()

    # --- Heap-i tap ---
    heap_start, heap_end = find_heap(pid)

    # --- Heap-i oxu ---
    heap_data = read_heap(pid, heap_start, heap_end)

    # --- String tap ---
    offset = heap_data.find(search_bytes)
    if offset == -1:
        print(f"[!] '{search_str}' heap-də tapılmadı.")
        sys.exit(1)

    found_addr = heap_start + offset
    print(f"[*] '{search_str}' tapıldı: ünvan 0x{found_addr:x} "
          f"(heap başından +{offset} bayt)")

    # --- Əvəz et (null terminator əlavə et, qalan baytları null ilə doldur) ---
    # Misal: "Holberton"(9 bayt) → "maroua\0\0\0"(9 bayt)
    padded = replace_bytes + b"\x00" * (len(search_bytes) - len(replace_bytes))

    write_heap(pid, found_addr, padded)

    print()
    print(f"[+] Uğurlu! '{search_str}' → '{replace_str}' əvəz edildi.")


if __name__ == "__main__":
    main()
