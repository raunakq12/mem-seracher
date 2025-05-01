import argparse
import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import (
    COLOR_RESET, COLOR_YELLOW, COLOR_GREEN,
    COLOR_CYAN, COLOR_MAGENTA, ascii_logo
)


CHUNK_SIZE = 4096

# ────────────────────────────────
# Argument Parser
# ────────────────────────────────
def parse_arguments():
    parser = argparse.ArgumentParser(description="Memory Dump Keyword Searcher (with multithreading + strings mode)")
    parser.add_argument("-f", "--file", required=True, help="Path to memory dump file")
    parser.add_argument("-k", "--keywords", required=True, nargs="+", help="Keyword(s) or regex pattern(s) to search")
    parser.add_argument("-c", "--context", type=int, default=20, help="Bytes of context to show around match")
    parser.add_argument("-o", "--output", help="Optional output log file")
    parser.add_argument("-i", "--ignore-case", action="store_true", help="Case-insensitive search")
    parser.add_argument("-s", "--use-strings", action="store_true", help="Use strings mode (ASCII only)")
    parser.add_argument("-w", action="store_true", help="Match whole words only (adds word boundaries)")
    return parser.parse_args()

# ────────────────────────────────
# Chunked Binary Reader
# ────────────────────────────────
def read_chunks(file_path, chunk_size=CHUNK_SIZE):
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield f.tell() - len(chunk), chunk

# ────────────────────────────────
# Strings Mode Integration
# ────────────────────────────────
def run_strings(file_path):
    try:
        result = subprocess.run(["strings", file_path], capture_output=True, text=True, check=True)
        return result.stdout
    except Exception as e:
        print(f"[!] Error running strings: {e}")
        return ""

def search_in_strings_output(strings_output, compiled_patterns):
    results = []
    for i, line in enumerate(strings_output.splitlines()):
        for pattern in compiled_patterns:
            if pattern.search(line):
                results.append((i, pattern.pattern, line))
    return results

# ────────────────────────────────
# Regex Match in Binary Chunks
# ────────────────────────────────
def search_in_chunk(chunk, offset, compiled_patterns, context):
    results = []
    last_positions = {}  # per-pattern deduplication

    for pattern in compiled_patterns:
        last_pos = -float('inf')
        for match in pattern.finditer(chunk):
            match_start = match.start()
            global_pos = offset + match_start

            # Skip if too close to last one (overlapping)
            if global_pos - last_pos < context * 2:
                continue

            start = max(match_start - context, 0)
            end = match.end() + context
            snippet = chunk[start:end]
            results.append((global_pos, pattern.pattern.decode(), snippet))

            last_pos = global_pos
        last_positions[pattern] = last_pos

    return results

# ────────────────────────────────
# Main Entry Point
# ────────────────────────────────
def main():
    args = parse_arguments()

    print(ascii_logo)
    print(f"{COLOR_CYAN}[*] Memory Scan Results:{COLOR_RESET}\n")

    flags = re.IGNORECASE if args.ignore_case else 0
    patterns = [bytes(k, "utf-8") if not args.use_strings else k for k in args.keywords]
    compiled_patterns = [re.compile(p, flags) for p in patterns]

    output_lines = []

    if args.use_strings:
        print(f"{COLOR_YELLOW}[*] Running in STRINGS mode...{COLOR_RESET}")
        strings_output = run_strings(args.file)
        results = search_in_strings_output(strings_output, compiled_patterns)

        for line_num, pattern, line in results:
            entry = f"{COLOR_YELLOW}=== MATCH FOUND ==={COLOR_RESET}\n" \
                    f"{COLOR_GREEN}[Pattern]: {pattern} | [Line]: {line_num}{COLOR_RESET}\n" \
                    f"[Snippet]: {COLOR_MAGENTA}{line.strip()}{COLOR_RESET}\n"
            print(entry)
            output_lines.append(entry)
    else:
        print(f"{COLOR_YELLOW}[*] Running multi-threaded binary search...{COLOR_RESET}")
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            futures = []
            for offset, chunk in read_chunks(args.file):
                futures.append(executor.submit(search_in_chunk, chunk, offset, compiled_patterns, args.context))

            for future in as_completed(futures):
                for pos, pattern, snippet in future.result():
                    highlighted = re.sub(
                        pattern,
                        f"{COLOR_MAGENTA}{pattern}{COLOR_RESET}",
                        snippet.decode('utf-8', 'ignore'),
                        flags=re.IGNORECASE if args.ignore_case else 0
                    )
                    entry = f"{COLOR_YELLOW}=== MATCH FOUND ==={COLOR_RESET}\n" \
                            f"{COLOR_GREEN}[Pattern]: {pattern} | [Offset]: {hex(pos)}{COLOR_RESET}\n" \
                            f"[Snippet]: {highlighted}\n"
                    print(entry)
                    output_lines.append(entry)
    if not output_lines:
        print(f"{COLOR_YELLOW}[!] No matches found for provided keyword(s).{COLOR_RESET}")
    else:
        print(f"{COLOR_GREEN}[*] Scan complete. {len(output_lines)} match(es) found.{COLOR_RESET}")
    if args.output:
        with open(args.output, "w") as out_file:
            for line in output_lines:
                out_file.write(re.sub(r"\x1b\[[0-9;]*m", "", line))  # strip ANSI codes
        print(f"\n{COLOR_CYAN}[+] Results saved to {args.output}{COLOR_RESET}")

if __name__ == "__main__":
    main()
