import pandas as pd
from tkinter_app.settings import MasterSettings
from ImageProcesser import ImageProcesser
from Plotter import Plotter
import os

class Dakar:
    """
    Orchestrates data loading and classification from a single MasterSettings object.
    """
    def __init__(self, settings: MasterSettings):
        
        self.settings = settings
        save_folder = self.settings.Dakar.save_folder
        analysis_name = self.settings.Dakar.analysis_name
        self.save_folder = os.path.join(save_folder,analysis_name)
        os.makedirs(self.save_folder, exist_ok=True)
        self.excel_file_name =self.settings.Dakar.analysis_name + '.xlsx'
        self.excel_path = os.path.join(self.save_folder,self.excel_file_name)
        self.raw_image_folder_path = self.settings.Dakar.data

    def combine_csv(self):
        """
        Finds and combines CSV files based on the foils_to_plot setting,
        and adds calculated columns.
        """

        foils_to_plot = self.settings.Dakar.foils_to_plot
        raw_data_folder = self.settings.Dakar.data
        all_dfs = []

        for state, foils in foils_to_plot.items():
            state_path = os.path.join(raw_data_folder, state)
            if not os.path.isdir(state_path):
                print(f"Warning: Directory for state '{state}' not found at '{state_path}'")
                continue

            for foil in foils:
                foil_path = os.path.join(state_path, foil)
                if not os.path.isdir(foil_path):
                    print(f"Warning: Directory for foil '{foil}' not found at '{foil_path}'")
                    continue

                csv_files = []
                for root, _, files in os.walk(foil_path):
                    for file in files:
                        if file.endswith('.csv'):
                            csv_files.append(os.path.join(root, file))

                if not csv_files:
                    print(f"Warning: No CSV file found for state '{state}', foil '{foil}' in '{foil_path}'")
                    continue

                if len(csv_files) > 1:
                    print(f"Warning: More than one CSV file found for state '{state}', foil '{foil}' in '{foil_path}'. Skipping.")
                    continue
                
                df = pd.read_csv(csv_files[0], header=None)
                df.columns = ["FOV", "FM SIZE", "POS X", "POS Y"]
                df['STATE'] = state
                df['FOIL'] = foil
                all_dfs.append(df)

        if not all_dfs:
            print("No CSV files found to combine.")
            return

        combined_df = pd.concat(all_dfs, ignore_index=True)

        min_fm_size = self.settings.Dakar.min_fm_size
        max_fm_size = self.settings.Dakar.max_fm_size
        combined_df = combined_df[combined_df['FM SIZE'].between(min_fm_size, max_fm_size)]
        image_width = int(self.settings.Dakar.image_width)
        image_height = int(self.settings.Dakar.image_height)

        combined_df['ROW INDEX'] = combined_df['FOV'].str[2].astype(int)
        combined_df['COLUMN INDEX'] = combined_df['FOV'].str[6].astype(int)
        combined_df['X PERCENTAGE'] = ((combined_df['COLUMN INDEX'] - 1) * 13264 + combined_df['POS X']) / image_width
        combined_df['Y PERCENTAGE'] = ((combined_df['ROW INDEX'] - 1) * 9180 + combined_df['POS Y']) / image_height
        combined_df['FOV NUMBER'] = (combined_df['ROW INDEX'] - 1) * 5 + combined_df['COLUMN INDEX']
        combined_df['ROW ID'] = combined_df.index + 1

        
        combined_df.to_excel(self.excel_path, index=False)
        print(f"Successfully combined {len(all_dfs)} CSV files with calculated columns into '{self.excel_path}'")


    def crop_FM_classify_top_bottom_from_excel(self, start_row=0, end_row=None):
        """
        Crops and classifies images based on data from the combined CSV file, iterating through states and foils.
        
        Args:
            start_row (int): Starting row index for CSV processing.
            end_row (int, optional): Ending row index for CSV processing. Defaults to None (process all rows).
        """

        df = pd.read_excel(self.excel_path)
        self.ImageProcesser = ImageProcesser(df)

        save_folder = os.path.join(self.save_folder,"Combined white and red images")
        os.makedirs(save_folder, exist_ok=True)

        df_to_process = df.iloc[start_row:end_row]
        
        if self.settings.Dakar.show_hyperlink:
            hyperlink_header = "WHITE RED IMAGE HYPERLINK"
            if hyperlink_header not in df_to_process.columns:
                df_to_process[hyperlink_header] = ''

        if "TOP BOTTOM" not in df_to_process.columns:
            df_to_process["TOP BOTTOM"] = ''


        states = df_to_process['STATE'].unique()
        
        for state in states:
            state_df = df_to_process[df_to_process['STATE'] == state]
            foils = state_df['FOIL'].unique()
            print(f"Processing state '{state}' with {len(foils)} unique foils: {foils}")
            
            for foil in foils:
                foil_df = state_df[state_df['FOIL'] == foil]
                fov_numbers = foil_df['FOV NUMBER'].unique()
                print(f"Processing foil '{foil}' with {len(fov_numbers)} FOVs: {fov_numbers}")
                
                for fov_number in fov_numbers:
                    matching_rows = foil_df[foil_df['FOV NUMBER'] == fov_number]
                    
                    white_image, red_image = self.ImageProcesser._match_white_red_image(
                        state, foil, fov_number, self.raw_image_folder_path
                    )
                    if white_image and red_image:
                        white_img , red_img = self.ImageProcesser._read_image([white_image,red_image])
                        for index, row in matching_rows.iterrows():
                            fm_size,x,y,state,name,fov,fov_number,row_id = row['FM SIZE'],row['POS X'],row['POS Y'],row['STATE'],row["FOIL"],row["FOV"],row["FOV NUMBER"],str(row["ROW ID"])
                            
                            cropped_white_img   = self.ImageProcesser._crop_image_base_on_coordinate(white_img,x,y,fm_size*3)
                            cropped_red_img   = self.ImageProcesser._crop_image_base_on_coordinate(red_img,x,y,fm_size*3)
                            combined_img = self.ImageProcesser._combine_image(cropped_white_img,cropped_red_img,direction = "horizontal")
                            combined_img = self.ImageProcesser._resize_keep_aspect(combined_img)
                        
                            title_string = f'{row_id}_{state}_{name}\nFOV Number: {fov_number}\nx: {x} y: {y}\nFMsize: {fm_size}'
                            file_name = row_id + " " + f'{state} {name} FOV Number_{fov_number} X_{x} Y_{y} FMsize_{fm_size}'
                            image_absolute_path = os.path.join(save_folder, file_name)
                            combined_img = self.ImageProcesser._overlay_text(title_string,combined_img,"top-left")
                            self.ImageProcesser._save_image_to_folder(save_folder,combined_img ,file_name)

                            if self.settings.Dakar.show_hyperlink:
                                image_absolute_path = os.path.abspath(image_absolute_path + ".png")
                                df_to_process.loc[index, hyperlink_header] = f'=HYPERLINK("{image_absolute_path}", "View")'

                    else:
                        print(f"Skipping row {row_id}: Images not found (White: {white_image}, Red: {red_image})")
                        
        df_to_process.to_excel(self.excel_path, index=False, engine='openpyxl')
        print(f"Successfully created Excel file with hyperlinks at '{self.excel_path}'")


    def crop_FM_check_background_fm(self):
        """
        Crops and classifies images based on data from the combined CSV file, iterating through states and foils.
        This version is optimized to reduce memory usage by reading and processing one image at a time.
        """
        save_folder = os.path.join(self.save_folder,"Combined different foil images")
        os.makedirs(save_folder, exist_ok=True)

        df = pd.read_excel(self.excel_path)
        self.ImageProcesser = ImageProcesser(df)

        if self.settings.Dakar.show_hyperlink:
            hyperlink_header = "DIFFERENT FOIL COMBINED HYPERLINK "
            if hyperlink_header not in df.columns:
                df[hyperlink_header] = ''

        df_to_process = df[df['TOP BOTTOM'].isin(['top', 'bottom'])]
        states = df_to_process['STATE'].unique()
        
        for state in states:
            state_df = df_to_process[df_to_process['STATE'] == state]
            fov_numbers = state_df['FOV NUMBER'].unique()
            print(f"Processing {state}  with {len(fov_numbers)} FOVs: {fov_numbers}")
            
            for fov_number in fov_numbers:
                matching_rows = state_df[state_df['FOV NUMBER'] == fov_number]
                
                image_paths = self.ImageProcesser._match_all_name_white_images(
                    state,  fov_number, self.raw_image_folder_path
                )
                image_paths = image_paths[:4] # Limit to a maximum of 4 images

                if image_paths:
                    for index, row in matching_rows.iterrows():
                        fm_size,x,y,state,name,fov,fov_number,row_id = row['FM SIZE'],row['POS X'],row['POS Y'],row['STATE'],row["FOIL"],row["FOV"],row["FOV NUMBER"],str(row["ROW ID"])
                        
                        cropped_parts = []
                        for image_path in image_paths:
                            try:
                                # Read one image at a time to save memory
                                single_img_list = self.ImageProcesser._read_image([image_path])
                                if not single_img_list:
                                    print(f"Warning: Could not read image {image_path}")
                                    continue
                                single_img = single_img_list[0]
                                
                                # Crop the single loaded image
                                cropped_part_list = self.ImageProcesser._crop_image_base_on_coordinate([single_img], x, y, fm_size * 3)
                                if not cropped_part_list:
                                    print(f"Warning: Could not crop image {image_path}")
                                    continue
                                cropped_parts.append(cropped_part_list[0])
                            except Exception as e:
                                print(f"An error occurred while processing {image_path} for row {row_id}: {e}")
                        
                        if not cropped_parts:
                            print(f"Skipping row {row_id} as no images could be cropped.")
                            continue

                        # Combine the collected cropped parts
                        combined_img = self.ImageProcesser._combine_image(*cropped_parts, direction="horizontal")
                        combined_img = self.ImageProcesser._resize_keep_aspect(combined_img)
                    
                        title_string = f'{row_id}_{state}_{name}\nFOV Number: {fov_number}\nx: {x} y: {y}\nFMsize: {fm_size}'
                        file_name = row_id + " " + f'{state} {name} FOV Number_{fov_number} X_{x} Y_{y} FMsize_{fm_size}'
                        combined_img = self.ImageProcesser._overlay_text(title_string,combined_img,"top-left")

                        image_absolute_path = os.path.join(save_folder, file_name)
                        self.ImageProcesser._save_image_to_folder(save_folder,combined_img ,file_name)

                        if self.settings.Dakar.show_hyperlink:
                            image_absolute_path = os.path.abspath(image_absolute_path + ".png")
                            df.loc[index, hyperlink_header] = f'=HYPERLINK("{image_absolute_path}", "View")'
                else:
                    print(f"Skipping FOV {fov_number} in state {state}: No images found.")
                        
        df.to_excel(self.excel_path, index=False, engine='openpyxl')
        print(f"Successfully created Excel file with hyperlinks at '{self.excel_path}'")


    def plot_compare_FM_summary(self):

        df = pd.read_excel(self.excel_path)
        self.Plotter = Plotter(df,self.settings.plotter)
        self.ImageProcesser = ImageProcesser(df)

        save_folder = os.path.join(self.save_folder,"Plot compare FM summary")
        os.makedirs(save_folder, exist_ok=True)

        before_state = self.settings.Dakar.before_state
        after_state = self.settings.Dakar.after_state

        if not before_state or not after_state:
            print("Warning: Before and/or After state not selected. Skipping comparison.")
            return

        # Get foils from the settings that are selected for the 'before' state
        foils_to_plot = self.settings.Dakar.foils_to_plot.get(before_state, [])

        for foil in foils_to_plot:
            # Check if the foil exists in the dataframe for both states to avoid errors
            before_foils = df[df['STATE'] == before_state]['FOIL'].unique()
            after_foils = df[df['STATE'] == after_state]['FOIL'].unique()

            if foil not in before_foils or foil not in after_foils:
                print(f"Warning: Foil '{foil}' not found in both states. Skipping comparison for this foil.")
                continue

            print(f"Comparing foil '{foil}' from '{before_state}' to '{after_state}'")
            
            before = self.Plotter.create_FM_position_plot(before_state, foil)
            after = self.Plotter.create_FM_position_plot(after_state, foil)
            generated_FM_changed_plots = self.Plotter.create_FM_change_plots(foil, before_state, after_state)
            added, removed, stayed = generated_FM_changed_plots
            summary = self.Plotter.create_changed_summary_plot(before, after, added, removed, stayed, foil, before_state, after_state)
            combined = self.ImageProcesser._combine_image_grid(before[0], after[0], summary, added[0], removed[0], stayed[0])
            self.ImageProcesser._save_image_to_folder(save_folder, combined, f'{foil} {before_state} to {after_state} summary')


    def plot_FM_summary(self):

        save_folder = os.path.join(self.save_folder,"Plot FM summary")
        os.makedirs(save_folder, exist_ok=True)
        df = pd.read_excel(self.excel_path)

        self.ImageProcesser = ImageProcesser(df)
        self.Plotter = Plotter(df,self.settings.plotter)

        foils_to_plot = self.settings.Dakar.foils_to_plot
        for state, foils in foils_to_plot.items():
      
            for foil in foils:
                generated_plot = self.Plotter.create_FM_position_plot(state,foil)
                self.ImageProcesser._save_image_to_folder(save_folder,generated_plot[0],state + " " + foil + ' plot')
                print(f"Plotted {state} {foil}")