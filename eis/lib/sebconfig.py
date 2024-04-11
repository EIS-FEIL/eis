"Safe Exam Browser (SEB) konfifaili lugemine ja kirjutamine"
import gzip
import zlib
import rncryptor
import plistlib
import os.path
import sys

class RNCryptor_modified(rncryptor.RNCryptor):
    def post_decrypt_data(self, data):
        data = data[:-(data[-1])]
        return data
    
def decrypt(filedata, password):
    "Konfi lugemine failist (parooliga krüptitud või krüptimata)"
    cryptor = RNCryptor_modified()
    file_content = gzip.decompress(filedata)
    prefix = file_content[:4]
    data = file_content[4:]
    if prefix == b'pswd':
        decrypted_data = cryptor.decrypt(data, password)
        #data = zlib.decompress(decrypted_data,15 + 32)
        data = decrypted_data
    elif prefix != b'plnd':
        raise Exception('Peab olema krüptimata või parooliga krüptitud fail (%s)' % prefix)
    return data

def generate():
    "Vaikimisi XML konf"
    #fn = os.path.join(os.path.dirname(__file__), 'sebsample.seb')
    fn = '/srv/eis/etc/sebsample.seb'
    with open(fn, 'rb') as f:
        data = f.read()
        return data

def user_agent(sooritus_id, testiruum_id):
    "SEB User-Agent sisse lisatav tunnus"
    return f'SEBEISTEST-{sooritus_id}-{testiruum_id}'

def check_plist(dataxml):
    "Kontrollitakse, kas on plisti kujul tekst"
    try:
        plistlib.loads(dataxml)
        return True
    except plistlib.InvalidFileException as ex:
        return False
    
def compress_plain(dataxml):
    "SEB faili loomine ilma krüptimata, aga pakitult"
    data = b'plnd' + gzip.compress(dataxml)
    return gzip.compress(data)

def compress_encrypt(dataxml, password):
    "SEB faili loomine parooliga krüptitult"
    cryptor = RNCryptor_modified()
    encrypted_data = b'pswd' + cryptor.encrypt(dataxml, password)
    return gzip.compress(encrypted_data)

if __name__ == '__main__':    
    op = sys.argv[1]
    if op == 'decrypt':
        # python sebconfig.py decrypt input.seb pwd
        fname = sys.argv[2]
        pwd = sys.argv[3]
        with open(fname, 'rb') as f:
            filedata = f.read()
            data0 = decrypt(filedata, pwd)
            print(data0.decode('utf-8'))
            
    elif op == 'plain':
        # python sebconfig.py plain output.seb
        fname = sys.argv[2]
        dataxml = generate()
        data1 = compress_plain(dataxml)
        with open(fname,'wb') as f:
            f.write(data1)
            
    elif op == 'encrypt':
        # python sebconfig.py encrypt output.seb pwd
        fname = sys.argv[2]
        pwd = sys.argv[3]
        dataxml = generate()
        data2 = compress_encrypt(dataxml, pwd)
        with open(fname,'wb') as f:
            f.write(data2)
    
