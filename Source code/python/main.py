
from datetime import datetime
from Dakar import Dakar
from settings import  MasterSettings
#.venv\Scripts\Activate.ps1
def main():
    settings = MasterSettings()
    dakar = Dakar(settings)

    start_time = datetime.now()
    
    #dakar.generate_excel_column_info()

    #dakar.crop_FM_classify_top_bottom(start_row=0, end_row=None)
    #dakar.crop_FM_check_background_fm(start_row=0, end_row=None)

    #dakar.plot_compare_FM_summary()
    dakar.plot_FM_summary()


    end_time = datetime.now()
    print(f'Total time is : {end_time - start_time}')


main()

