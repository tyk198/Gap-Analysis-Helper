from dataclasses import dataclass, field
from typing import Dict, Any,List
import os 
import json
from dacite import from_dict, Config

@dataclass
class crop_FM_classify_top_bottom_Settings:

    image_output_folder: str = field(
        default=r'result\images\white_red_combined',
        metadata={
            "tooltip": "Path to the folder containing cropped and combined images", 
            "setting_type": "folder",
            "label": "Image Output Folder"
        }
    )
    excluded_fovs: List = field(
        default_factory=lambda: [25, 26, 29, 30],
        metadata={"tooltip": "List of FOV numbers to exclude", "label": "Excluded FOVs"}
    )

@dataclass
class crop_FM_check_background_fm_settings:

    image_output_folder: str = field(
        default=r'result\images\Different_foil_combined',
        metadata={
            "tooltip": "Path to the folder containing cropped and combined images", 
            "setting_type": "folder",
            "label": "Image Output Folder"
        }
    )

@dataclass
class plot_FM_summary_settings:

    image_output_folder: str = field(
        default=r'result\images\FM_plot',
        metadata={
            "tooltip": "Path to the folder containing cropped and combined images", 
            "setting_type": "folder",
            "label": "Image Output Folder"
        }
    )



@dataclass
class plot_complete_FM_summary_settings:

    output_folder: str = field(
        default=r'result\images\ComparePlot',
        metadata={
            "tooltip": "Path to the folder containing complete FM summary files", 
            "setting_type": "folder",
            "label": "Output Folder"
        }
    )

@dataclass
class DakarSettings:
    
    

    data: str = field(
        default=r'data/Raw data',
        metadata={
            "tooltip": "Path to the general data folder",
            "setting_type": "folder",
            "label": "Raw Data Folder"
        }
    )

    foils_to_plot : Dict =  field(
        default_factory=dict,
        metadata={"label": "Foils to Plot", "widget_type": "foils_selector"}
    )

    excel_folder: str = field(
        default=r'result/csv',
        metadata={
            "tooltip": "Path to the Combined Excel file for Dakar data", 
            "setting_type": "folder",
            "label": "Excel Path"
        }
    )

    analysis_name: str = field(
        default=r'Gap Analysis',
        metadata={
            "tooltip": "The excel file name", 
            "label": "Excel file name"
        }
    )

    save_folder: str = field(
        default=r'result',
        metadata={
            "tooltip": "The folder to save all the combined images and plot", 
            "setting_type": "folder",
            "label": "Save folder"
        }
    )





    image_width: str = field(
        default=66320,
        metadata={"tooltip": "The width of image", "label": "Image Width", "layout_group": "image_size"}
    )
    image_height: str = field(
        default=55080,
        metadata={"tooltip": "The height of image", "label": "Image Height", "layout_group": "image_size"}
    )

    min_fm_size: int = field(
        default=100,
        metadata={"tooltip": "Minimum FM size to filter", "label": "Min FM Size", "layout_group": "fm_size"}
    )
    max_fm_size: int = field(
        default=700,
        metadata={"tooltip": "Maximum FM size to filter", "label": "Max FM Size", "layout_group": "fm_size"}
    )

    crop_FM_classify_top_bottom :crop_FM_classify_top_bottom_Settings = field(
        default_factory=crop_FM_classify_top_bottom_Settings,
        metadata={"label": "Crop for Top/Bottom Classification"}
    )

    crop_FM_check_background_fm:crop_FM_check_background_fm_settings = field(
        default_factory=crop_FM_check_background_fm_settings,
        metadata={"label": "Crop for Background FM Check"}
    )

    plot_compare_FM_summary :plot_complete_FM_summary_settings = field(
        default_factory=plot_complete_FM_summary_settings,
        metadata={"label": "Plot Complete FM Summary"}
    )

    plot_FM_summary: plot_FM_summary_settings = field(
        default_factory=plot_FM_summary_settings,
        metadata={"label": "Plot FM Summary"}
    )

@dataclass
class PlotterSettings:
    background_image_path: str = field(
        default='data/original_resize.jpg',
        metadata={
            "tooltip": "Path to the background image for plots", 
            "setting_type": "file",
            "label": "Background Image Path"
        }
    )
    figure: Dict[str, Any] = field(
        default_factory=lambda: {
            "figsize": [17, 12],
            "margin_left": 0.15
        },
        metadata={"tooltip": "Figure settings (e.g., size, margins)", "label": "Figure"}
    )
    legend: Dict[str, Any] = field(
        default_factory=lambda: {
            "location": "upper left",
            "anchor": [-0.15, 1.0],
            "fontsize": 12,
            "title": "Legend",
            "title_fontsize": 14
        },
        metadata={"tooltip": "Legend settings (e.g., location, font size)", "label": "Legend"}
    )
    points: Dict[str, Any] = field(
        default_factory=lambda: {
            "marker_size": 80.0,
            "bottom_color": "blue",
            "top_color": "red"
        },
        metadata={"tooltip": "Point settings (e.g., marker size, colors)", "label": "Points"}
    )
    shape_mapping: Dict[str, Any] = field(
        default_factory=lambda: {
            "triangle": {"label": "100-200", "marker": "^", "min_size": 100, "max_size": 200},
            "square": {"label": "200-300", "marker": "s", "min_size": 200, "max_size": 300},
            "pentagon": {"label": "300-400", "marker": "p", "min_size": 300, "max_size": 400},
            "hexagon": {"label": "400-500", "marker": "h", "min_size": 400, "max_size": 500},
            "octagon": {"label": "500-600", "marker": "8", "min_size": 500, "max_size": 600},
            "other": {"label": " >600", "marker": "o", "min_size": None, "max_size": None}
        },
        metadata={"tooltip": "Mapping of shapes to plot properties", "label": "Shape Mapping"}
    )
    summary_text: Dict[str, Any] = field(
        default_factory=lambda: {
            "location": [-0.15, 0.65],
            "fontsize": 12,
            "box_props": {
                "alpha": 0.7,
                "boxstyle": "round,pad=0.5",
                "facecolor": "white"
            }
        },
        metadata={"tooltip": "Summary text settings (e.g., location, font size)", "label": "Summary Text"}
    )

@dataclass
class MasterSettings:
    Dakar: DakarSettings = field(
        default_factory=DakarSettings,
        metadata={"label": "Dakar Settings", "visible_in_ui": True}
    )
    plotter: PlotterSettings = field(
        default_factory=PlotterSettings,
        metadata={"visible_in_ui": False}
    )

from dataclasses import fields, is_dataclass, asdict
def load_from_json(file_path: str) -> MasterSettings:
    """Loads settings from a JSON file and returns a new MasterSettings instance."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        print(f"Successfully loaded settings from {file_path}")
    except FileNotFoundError:
        print("settings file not found, use default settings")
        return MasterSettings()
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {file_path}, using default settings instead.")
        return MasterSettings()
    
    def create_from_dict(cls, data_dict):
        field_names = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data_dict.items() if k in field_names}
        
        for f in fields(cls):
            if is_dataclass(f.type) and f.name in filtered_data:
                filtered_data[f.name] = create_from_dict(f.type, filtered_data[f.name])
        
        return cls(**filtered_data)

    return create_from_dict(MasterSettings, data)




