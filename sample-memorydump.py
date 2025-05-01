import os
import random
import string

def generate_fake_memory_dump(filename="fake_memory.raw", size_mb=50):
    with open(filename, "wb") as f:
        for _ in range(size_mb * 1024):  # Write 1024 bytes * size_mb
            block = ''.join(random.choices(string.printable, k=1024))
            f.write(block.encode('utf-8'))

        # Add known patterns for testing
        f.write(b"\npassword=supersecret123\n")
        f.write(b"\nlogin_token=xyz789\n")
        f.write(b"\nflag{example_flag}\n")

generate_fake_memory_dump()



                                                                                                                           