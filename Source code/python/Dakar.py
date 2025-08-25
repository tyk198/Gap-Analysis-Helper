from numpy import full
import pandas as pd
from settings import MasterSettings
from ImageProcesser import ImageProcesser
from Plotter import Plotter
from ExcelProcesser import ExcelProcesser
import os
import openpyxl

class Dakar:
    """
    Orchestrates data loading and classification from a single MasterSettings object.
    """
    def __init__(self, settings: MasterSettings):

        self.settings = settings
        self.data = pd.read_excel(self.settings.Dakar.Excel_input_path, sheet_name='ALL DATA').copy()
        self.testing_excel_path = self.settings.Dakar.run_excel.input_file
        self.wb = openpyxl.load_workbook(self.testing_excel_path,data_only=True)

        self.ImageProcesser = ImageProcesser(self.data)
        self.Plotter = Plotter(self.data,self.settings.plotter)
        self.ExcelProcesser = ExcelProcesser()


    def run_excel_openpyxl(self):
        """
        Runs the Excel processing workflow using openpyxl.
        """
        testing_excel_path = self.settings.Dakar.run_excel.input_file
        target_ws= self.ExcelProcesser.read_and_copy_worksheet(self.wb)
        self.ExcelProcesser.add_column_with_formula(target_ws, "ROW INDEX", '=VALUE(MID({cell},3,1))', {"cell": 1})
        self.ExcelProcesser.add_column_with_formula(target_ws, "COLUMN INDEX", '=VALUE(MID({cell},7,1))', {"cell": 1})
        self.ExcelProcesser.add_column_with_formula(target_ws, "X PERCENTAGE", '=(({col_I}-1)*13264 + {col_C}) / 66320', {'col_I': 'I', 'col_C': 'C'})
        self.ExcelProcesser.add_column_with_formula(target_ws, "Y PERCENTAGE", '=(({col_H}-1)*9180 + {col_D}) / 55080', {'col_H': 'H', 'col_D': 'D'})
        self.ExcelProcesser.add_column_with_formula(target_ws, "FOV NUMBER", '=({col_H}-1)*5 + {col_I}', {'col_H': 'H', 'col_I': 'I'})
        self.ExcelProcesser.create_table(target_ws)
        self.wb.save(testing_excel_path)


    def crop_FM_classify_top_bottom(self, start_row=0, end_row=None):
        target_ws  = self.wb["copy data"]
        raw_image_folder_path = self.settings.Dakar.crop_FM_classify_top_bottom.raw_image_input_folder
        output_folder = self.settings.Dakar.crop_FM_classify_top_bottom.image_output_folder
        min_fm_size = self.settings.Dakar.crop_FM_classify_top_bottom.min_fm_size
        max_fm_size = self.settings.Dakar.crop_FM_classify_top_bottom.max_fm_size
        testing_excel_path = self.settings.Dakar.run_excel.input_file

        self.ExcelProcesser.add_column_header(target_ws,"Hyperlink")
        df_slice = self.data.iloc[start_row:end_row]
        for index, row in df_slice.iterrows():
            fm_size,x,y,state,name,fov,fov_number,row_id = row['FM SIZE'],row['POS X'],row['POS Y'],row['STATE'],row["NAME"],row["FOV"],row["FOV NUMBER"],str(row["ROW ID"])
            if fm_size < min_fm_size or fm_size > max_fm_size :
                continue
            top_bottom = row['TOP BOTTOM']

            #if top_bottom != "top" and top_bottom != "bottom":
            #    continue
            white_image, red_image = self.ImageProcesser._match_white_red_image(row,raw_image_folder_path)
            white_img , red_img = self.ImageProcesser._read_image([white_image,red_image])
            white_img   = self.ImageProcesser._crop_image_base_on_coordinate(white_img,x,y,fm_size*3)
            red_img   = self.ImageProcesser._crop_image_base_on_coordinate(red_img,x,y,fm_size*3)
            combined_img = self.ImageProcesser._combine_image(white_img,red_img,direction = "horizontal")
            combined_img = self.ImageProcesser._resize_keep_aspect(combined_img)
           
            title_string = f'{row_id}_{state}_{name}\nFOV: {fov}\nFOV Number: {fov_number}\nx: {x} y: {y}\nFMsize: {fm_size}'
            file_name = row_id + " " + f'{state} {name} {fov} FOV Number_{fov_number} X_{x} Y_{y} FMsize_{fm_size}'
            image_absolute_path = os.path.join(output_folder, file_name)
            combined_img = self.ImageProcesser._overlay_text(title_string,combined_img,"top-left")
            #self.ImageProcesser.show_image(combined_img,window_name = title_string ,scale_resize  = 1)

            self.ImageProcesser._save_image_to_folder(output_folder,combined_img ,file_name)

            image_absolute_path = os.path.abspath(image_absolute_path + ".png")
            excel_absolute_path = os.path.abspath(self.testing_excel_path)


            self.ExcelProcesser.add_hyperlink_to_column(target_ws,image_absolute_path,excel_absolute_path,row_id)
            self.wb.save(testing_excel_path)
            

    def crop_FM_check_background_fm(self, start_row=0, end_row=None):
        raw_image_folder_path = self.settings.Dakar.crop_FM_check_background_fm.raw_image_input_folder
        output_folder = self.settings.Dakar.crop_FM_check_background_fm.image_output_folder
        min_fm_size = self.settings.Dakar.crop_FM_classify_top_bottom.min_fm_size
        max_fm_size = self.settings.Dakar.crop_FM_classify_top_bottom.max_fm_size
        valid_options =  ["top","bottom"]

        df_slice = self.data.iloc[start_row:end_row]
        for index, row in df_slice.iterrows():
            fm_size,x,y,state,name,fov,fov_number,row_id = row['FM SIZE'],row['POS X'],row['POS Y'],row['STATE'],row["NAME"],row["FOV"],row["FOV NUMBER"],str(row["ROW ID"])
            top_bottom = row['TOP BOTTOM']
            if fm_size < min_fm_size or fm_size > max_fm_size :
                continue
            if top_bottom != "top" and top_bottom != "bottom":
                continue
            
            images = self.ImageProcesser._match_all_name_white_images(row,raw_image_folder_path)

            images = self.ImageProcesser._read_image(images)
            zoomout_images   = self.ImageProcesser._crop_image_base_on_coordinate(images,x,y,fm_size * 3)
            images   = self.ImageProcesser._crop_image_base_on_coordinate(images,x,y,fm_size)

            zoomout_combined_img = self.ImageProcesser._combine_image(*zoomout_images,direction = "horizontal")
            combined_img = self.ImageProcesser._combine_image(*images,direction = "horizontal")

            zoomout_combined_img = self.ImageProcesser._resize_keep_aspect(zoomout_combined_img)
            combined_img = self.ImageProcesser._resize_keep_aspect(combined_img)

            final_combined_img = self.ImageProcesser._combine_image(zoomout_combined_img,combined_img,direction = "vertical")



            title_string = f'{row_id}_{state}\nFOV: {fov}\nFOV Number: {fov_number}\nx: {x} y: {y}\nFMsize: {fm_size}'
            file_name = f'{state} {fov} FOV Number_{fov_number} X_{x} Y_{y} FMsize_{fm_size}'

            combined_img = self.ImageProcesser._overlay_text(title_string,final_combined_img,"top-left")
            #self.ImageProcesser.show_image(combined_img,window_name = title_string ,scale_resize  = 1)
            self.ImageProcesser._save_image_to_folder(output_folder,final_combined_img ,row_id +" "+ file_name)





    def plot_complete_FM_summary(self):

        output_folder = self.settings.Dakar.plot_complete_FM_summary.output_folder

        tb_filter = ['top', 'bottom']
        names_to_plot = self.data['NAME'].unique()
        #states = ["BeforeFinalTest", "AfterFinalTest", "AfterFinalVI"]
        states = ["AfterFoilDetach", "AfterLaserCut"]

        for name in names_to_plot:
            for i in range(len(states) - 1):
                state1, state2 = states[i], states[i + 1]

                before = self.Plotter.create_FM_position_plot(name,state1,tb_filter)
                after = self.Plotter.create_FM_position_plot(name,state2,tb_filter)
                generated_FM_changed_plots = self.Plotter.create_FM_change_plots(name, state1, state2)
                added,removed,stayed  = generated_FM_changed_plots
                summary = self.Plotter.create_summary_plot(before,after,added,removed,stayed,name,state1,state2)
                combined = self.ImageProcesser._combine_image_grid(before[0],after[0], summary,added[0],removed[0],stayed[0])
                self.ImageProcesser._save_image_to_folder(output_folder,combined,name+' '+ state1+" to "+state2 + ' summary')
