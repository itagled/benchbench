def crc16(data: bytes) -> bytes:
    """Computes a Modbus CRC16 over the given bytes."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return bytes([crc >> 8, crc & 0xFF])

def compress(data: bytes) -> bytes:
    """
    Compresses data using a simple custom LZ77 algorithm.
    The stream consists of control bytes and token sequences.
    Each bit in a control byte dictates the type of the next token:
      0 = Literal (1 byte)
      1 = Backreference (2 bytes)
    """
    out = bytearray()
    i = 0
    while i < len(data):
        control_byte_idx = len(out)
        out.append(0)
        control_byte = 0

        for bit in range(8):
            if i >= len(data):
                break

            # Find longest match
            match_len = 0
            match_dist = 0
            start_window = max(0, i - 4095) # 12-bit distance
            for j in range(start_window, i):
                l = 0
                while l < 18 and i + l < len(data) and data[j + l] == data[i + l]:
                    l += 1
                if l > match_len:
                    match_len = l
                    match_dist = i - j

            if match_len >= 3:
                # Backreference
                control_byte |= (1 << (7 - bit))
                # Encode 12-bit distance and 4-bit length
                # Byte 1: lower 8 bits of distance
                # Byte 2: upper 4 bits of distance | (length - 3)
                out.append(match_dist & 0xFF)
                out.append(((match_dist >> 8) << 4) | (match_len - 3))
                i += match_len
            else:
                # Literal
                out.append(data[i])
                i += 1

        out[control_byte_idx] = control_byte
    return bytes(out)

class DecompressionError(Exception): pass

def decompress(comp: bytes, uncompressed_size: int) -> bytes:
    """
    Decompresses data compressed by the custom LZ77 algorithm.
    Raises DecompressionError if the stream is malformed.
    """
    out = bytearray()
    i = 0
    while i < len(comp) and len(out) < uncompressed_size:
        control_byte = comp[i]
        i += 1
        for bit in range(8):
            if len(out) >= uncompressed_size:
                break
            if i >= len(comp):
                if len(out) < uncompressed_size:
                    raise DecompressionError("Unexpected EOF")
                break
            is_backref = (control_byte & (1 << (7 - bit))) != 0
            if is_backref:
                if i + 1 >= len(comp):
                    raise DecompressionError("Truncated backref")
                b1 = comp[i]
                b2 = comp[i+1]
                i += 2
                dist = b1 | ((b2 >> 4) << 8)
                length = (b2 & 0x0F) + 3

                if dist == 0 or dist > len(out):
                    raise DecompressionError(f"Invalid distance {dist}")

                for _ in range(length):
                    out.append(out[-dist])
            else:
                out.append(comp[i])
                i += 1
    return bytes(out)
