import os.path
import argparse
from dotenv import load_dotenv

from pyicloud import PyiCloudService

print('iCloud python scrypt - Download RAW and JPG Photos')

# Args
parser = argparse.ArgumentParser()
parser.add_argument('-album_name', dest='album_name', type=str)
parser.add_argument('-destination', dest='path', type=str)
args = parser.parse_args()

if not args.album_name:
    print('Need -album_name argument') 
    exit()

if not args.path:
    print('Need -destination argument') 
    exit()

load_dotenv()

def get_jpg_version(versions):
    version = ''
    for key in versions.keys():
        if versions[key]['type'] == 'public.jpeg':
            if version == '': 
                version = key
            else:
                if versions[key]['size'] > versions[version]['size']:
                    version = key

    return version

def get_extention(type_file):

    if type_file == 'com.nikon.raw-image':
        return '.NEF'

    if type_file == 'com.sony.arw-raw-image':
        return '.ARW'
    
    if type_file == 'public.jpeg':
        return '.JPG'

    if type_file == 'com.adobe.raw-image':
        return '.DNG'

    return '.' + type_file

print("Authentification...")
# Connectez-vous à iCloud avec votre identifiant Apple et votre mot de passe.
api = PyiCloudService(os.environ['USERNAME'], os.environ['PASSWORD'])

if api.requires_2fa:
    print("Two-factor authentication required.")
    code = input("Enter the code you received of one of your approved devices: ")
    result = api.validate_2fa_code(code)
    print("Code validation result: %s" % result)

    if not result:
        print("Failed to verify security code")
        sys.exit(1)

    if not api.is_trusted_session:
        print("Session is not trusted. Requesting trust...")
        result = api.trust_session()
        print("Session trust result %s" % result)

        if not result:
            print("Failed to request trust. You will likely be prompted for the code again in the coming weeks")
elif api.requires_2sa:
    import click
    print("Two-step authentication required. Your trusted devices are:")

    devices = api.trusted_devices
    for i, device in enumerate(devices):
        print(
            "  %s: %s" % (i, device.get('deviceName',
            "SMS to %s" % device.get('phoneNumber')))
        )

    device = click.prompt('Which device would you like to use?', default=0)
    device = devices[device]
    if not api.send_verification_code(device):
        print("Failed to send verification code")
        sys.exit(1)

    code = click.prompt('Please enter validation code')
    if not api.validate_verification_code(device, code):
        print("Failed to verify verification code")
        sys.exit(1)

print('Authentification succeed !')

# Obtenir tous les albums
# albums = api.photos.albums

# for album in albums:
#     print(album)

# album_name = 'RAW'

# Obtenez l'album photo avec l'identifiant spécifié.
print('Get photos in album :' , args.album_name)
album = api.photos.albums.get(args.album_name)
# album = api.photos.all

# Accédez à la liste des photos de l'album.
photos = album.photos

# Affichez les noms de fichier des 10 premières photos de l'album.
count = 0
limit = 1
for photo in photos:
    if count < limit:
        # print("id: ",photo.id, "| filename: ", photo.filename, "| size (Bytes): ", photo.size, "| created: ", photo.created)

        # Display progression
        progress = '(' + str(count + 1) + '/' + str(limit) + ')'

        raw_version = 'original'
        if 'original_alt' in photo.versions.keys():
            if photo.versions['original']['size'] < photo.versions['original_alt']['size']:
                raw_version = 'original_alt'

        jpg_version = get_jpg_version(photo.versions)

        if not raw_version in photo.versions.keys():
                print('Photo do not have RAW version :', raw_version)
                print('keys :', photo.versions.keys())
                exit()
        
        # print('RAW Version :', raw_version, photo.versions[raw_version])

        if not jpg_version in photo.versions.keys():
                print('Photo do not have JPG version :', jpg_version)
                print('keys :', photo.versions.keys())
                exit()

        # print('JPG Version :', jpg_version, photo.versions[jpg_version])

        if photo.versions[raw_version]['type'] != 'public.jpeg':

            # Import JPG Format
            extention = get_extention(photo.versions[jpg_version]['type'])
            
            filename_jpg = photo.versions[jpg_version]['filename'].split('.')[0] + '_' + str(round(photo.created.timestamp())) + extention
            path_jpg = args.path + '/JPG/' + filename_jpg
            
            if not os.path.exists(path_jpg):
                print('Download JPG file :', filename_jpg, '| size (Mb):', round((photo.versions[jpg_version]['size'] / (1024 * 1024)), 2), progress)
                download = photo.download(jpg_version)
                with open(path_jpg, 'wb') as jpg_file:
                    jpg_file.write(download.raw.read())

            else:
                # Exist JPG File
                if os.stat(path_jpg).st_size == photo.versions[jpg_version]['size']:
                    print('JPG File exist :', filename_jpg, progress)

                else:
                    print('Redownload JPG file :', filename_jpg, '| size (Mb):', round((photo.versions[jpg_version]['size'] / (1024 * 1024)), 2), progress)
                    download = photo.download(jpg_version)
                    with open(path_jpg, 'wb') as jpg_file:
                        jpg_file.write(download.raw.read())

            # Import RAW Format
            extention = get_extention(photo.versions[raw_version]['type'])

            filename_raw = photo.versions[raw_version]['filename'].split('.')[0] + '_' + str(round(photo.created.timestamp())) + extention
            path_raw = args.path + '/RAW/' + filename_raw

            if not os.path.exists(path_raw):
                print('Download RAW file :', filename_raw, '| size (Mb):', round((photo.versions[raw_version]['size'] / (1024 * 1024)), 2), progress)
                download = photo.download(raw_version)
                with open(path_raw, 'wb') as raw_file:
                  raw_file.write(download.raw.read())

            else:
                # Exist RAW File
                if os.stat(path_raw).st_size == photo.versions[raw_version]['size']:
                    print('RAW File exist :', filename_raw, progress)

                else:
                    print('Redownload RAW file :', filename_raw, '| size (Mb):', round((photo.versions[raw_version]['size'] / (1024 * 1024)), 2), progress)
                    download = photo.download(raw_version)
                    with open(path_raw, 'wb') as raw_file:
                        raw_file.write(download.raw.read())

            # Delete File
            # photo.delete()
            # print('Photo is delete :', photo.filename, progress)

        else:
            print('This photo do not have RAW format :', photo.filename, progress)

        count += 1
    else:
        break

print("End !")