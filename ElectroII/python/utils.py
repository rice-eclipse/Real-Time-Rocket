
def big_endian_add(bytes):
    """
    Add an array of bytes into an int the little-endian way.
    """
    output = 0
    for i in range(len(bytes)):
        output += bytes[i] << 8*(len(bytes)-i-1)
    return output
