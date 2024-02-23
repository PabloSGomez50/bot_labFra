import json
import youtube_dl
import os

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    # 'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn',
}

def main():
    while (url := input('Youtube url: ')).lower() != 'exit':
        try:
            with youtube_dl.YoutubeDL(ytdl_format_options) as ytdl:
                data = ytdl.extract_info(url, download=False)

            if 'title' in data:
                print(f'Saving "{data["title"]}" content in json file')
                file_path = f'youtube_info/{data["title"]}.json'
                if not os.path.exists(file_path):
                    print('Direccion actual:', os.getcwd())
                    print(os.path.dirname(file_path))
                    os.mkdir(os.path.dirname(file_path))

                with open(file_path, 'w') as fp:
                    json.dump(data, fp, indent=4)
        except KeyError as e:
            print('No se pudo obtener la key:', e)
        except Exception as e:
            print('Error no procesado:', e)

if __name__ == '__main__':
    main()