import anvil.server
from anvil import URLMedia
import auto_batch.tables.query as q
from auto_batch.tables import app_tables


class AssetFiles:
    names = set([
        'nycnvc_feelings_needs',
        'bowl_struck_wav',
        'doorbell_mp3',
        'doorbell_wav',
    ])
    
    def __init__(self):
        self.nycnvc_feelings_needs = URLMedia('_/theme/for_files_table/nycnvc_feelings_needs.pdf')
        self.bowl_struck_wav = URLMedia('_/theme/for_files_table/2166__suburban-grilla__bowl-struck.wav')
        self.doorbell_mp3 = URLMedia('_/theme/for_files_table/doorbell-1.mp3')
        self.doorbell_wav = URLMedia('_/theme/for_files_table/doorbell-1.wav')


def store_files_if_missing():
    files = app_tables.files.search(q.fetch_only("name"))
    missing_names = AssetFiles.names - {row['name'] for row in files}
    if missing_names:
        send_assets_to_data_tables(missing_names)


def send_assets_to_data_tables(missing_names):
    files = AssetFiles()
    anvil.server.call('store_files', {name: getattr(files, name) for name in missing_names})
