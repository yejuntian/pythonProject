import hashlib
import zipfile


def md5_byte_to_str(md5):
    return ''.join('{:02x}'.format(b) for b in md5)


import base64


def get_base64(fpath):
    # IX0XNcGamF83m++g59HaKw==
    bytes = get_md5(fpath)
    md5 = md5_byte_to_str(bytes)
    print(">>>>>>>>>md5:", md5)  # c7319de7e3d51821a0de4de37f029c73

    encode = base64.b64encode(bytes)
    s = encode.decode()
    print(">>>>>>>>>s:", s)

    decode = base64.b64decode(s)
    d = decode.hex()
    print(">>>>>>>>>b:", d)


def get_md5(path):
    zip_file = None
    input_stream = None
    bytes = b''
    try:
        print(">>>>>>>>>path:", path)
        zip_file = zipfile.ZipFile(path)
        entry = zip_file.getinfo("classes.dex")
        input_stream = zip_file.open(entry)
        digest = hashlib.md5()
        buffer = input_stream.read(0x2000)
        while buffer:
            digest.update(buffer)
            buffer = input_stream.read(0x2000)

        print(">>>>>>>>>do2:")
        bytes = digest.digest()
    except (IOError) as e:
        print(e)
        print(">>>>>>>>>do3:")
    finally:
        if input_stream is not None:
            try:
                input_stream.close()
            except IOError:
                pass
        if zip_file is not None:
            try:
                zip_file.close()
            except IOError:
                pass
    print(">>>>>>>>>do4:")
    print(">>>>>>>>>bytes:", bytes)
    return bytes


if __name__ == "__main__":
    fpath = "/Users/shareit/Downloads/WhatsApp_2.22.22.80.apk"
    get_base64(fpath)
