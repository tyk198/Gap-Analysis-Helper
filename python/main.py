
from datetime import datetime
from Dakar import Dakar
from app.settings_service import SettingsService
#from app.settings import load_from_json

def main():
    settings_service = SettingsService()
    settings = settings_service.load_from_json(r'python\tkinter_app\settings.json')
    dakar = Dakar(settings)

    start_time = datetime.now()
    dakar.combine_csv()
    dakar.crop_FM_classify_top_bottom_from_excel(start_row=0, end_row=None)

    #dakar.crop_FM_check_background_fm()

    #dakar.plot_compare_FM_summary()
    #dakar.plot_FM_summary()


    end_time = datetime.now()
    print(f'Total processed time is : {end_time - start_time}')


main()

