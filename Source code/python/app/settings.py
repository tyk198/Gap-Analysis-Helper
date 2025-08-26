from dataclasses import dataclass, field,asdict
from typing import Dict, Any,List
import os 
import json


@dataclass
class crop_FM_classify_top_bottom_Settings:
    raw_image_input_folder: str = field(
        default=r'data',
        metadata={
            "tooltip": "Path to the folder containing raw images for processing", 
            "setting_type": "folder",
            "label": "Raw Image Input Folder"
        }
    )

    image_output_folder: str = field(
        default=r'Result\crop_to_classify_top_bottom\incomingstate\v1',
        metadata={
            "tooltip": "Path to the folder containing cropped and combined images", 
            "setting_type": "folder",
            "label": "Image Output Folder"
        }
    )
    min_fm_size: int = field(
        default=100,
        metadata={"tooltip": "Minimum FM size to filter", "label": "Min FM Size"}
    )
    max_fm_size: int = field(
        default=700,
        metadata={"tooltip": "Maximum FM size to filter", "label": "Max FM Size"}
    )
    excluded_fovs: List = field(
        default_factory=lambda: [25, 26, 29, 30],
        metadata={"tooltip": "List of FOV numbers to exclude", "label": "Excluded FOVs"}
    )

@dataclass
class crop_FM_check_background_fm_settings:
    raw_image_input_folder: str = field(
        default=r'data',
        metadata={
            "tooltip": "Path to the folder containing raw images for processing", 
            "setting_type": "folder",
            "label": "Raw Image Input Folder"
        }
    )

    image_output_folder: str = field(
        default=r'Result\Crop_to_classify_background\incomingstate',
        metadata={
            "tooltip": "Path to the folder containing cropped and combined images", 
            "setting_type": "folder",
            "label": "Image Output Folder"
        }
    )

    min_fm_size: int = field(
        default=100,
        metadata={"tooltip": "Minimum FM size to filter", "label": "Min FM Size"}
    )
    max_fm_size: int = field(
        default=2000,
        metadata={"tooltip": "Maximum FM size to filter", "label": "Max FM Size"}
    )

@dataclass
class plot_FM_summary_settings:

    image_output_folder: str = field(
        default=r'Result\FM_plot',
        metadata={
            "tooltip": "Path to the folder containing cropped and combined images", 
            "setting_type": "folder",
            "label": "Image Output Folder"
        }
    )

    foils_to_plot : Dict =  field(
        default_factory = lambda: {
            "IncomingState": ["incomingfoil1","incomingfoil2","incomingfoil3","incomingfoil4","incomingfoil5"],
            "ManualDetachState": ["ManualDetach1","ManualDetach2","ManualDetach3","ManualDetach4","ManualDetach5"]
        },
        metadata={"label": "Foils to Plot", "widget_type": "foils_selector"}
    )

@dataclass
class plot_complete_FM_summary_settings:

    output_folder: str = field(
        default=r'Result\SummaryPlot\V3',
        metadata={
            "tooltip": "Path to the folder containing complete FM summary files", 
            "setting_type": "folder",
            "label": "Output Folder"
        }
    )

@dataclass
class DakarSettings:

    Excel_input_path: str = field(
        default=r'CSV\ManualDetach Gap Analysis.xlsx',
        metadata={
            "tooltip": "Path to the Excel file for Dakar data", 
            "setting_type": "file",
            "label": "Excel Input Path"
        }
    )

    Excel_copy_path: str = field(
        default=r'CSV\ManualDetach Gap Analysis_copy.xlsx',
        metadata={
            "tooltip": "Path to the Excel file for Dakar data", 
            "setting_type": "file",
            "label": "Excel Copy Path"
        }
    )
    worksheet_to_read: str = field(
        default='copy data2',
        metadata={"tooltip": "The name of the worksheet to read", "label": "Worksheet to Read"}
    )

    image_width: str = field(
        default=66320,
        metadata={"tooltip": "The width of image", "label": "Image Width"}
    )
    image_height: str = field(
        default=55080,
        metadata={"tooltip": "The height of image", "label": "Image Height"}
    )

    data: str = field(
        default=r'data/Raw data',
        metadata={
            "tooltip": "Path to the general data folder",
            "setting_type": "folder",
            "label": "Data Folder"
        }
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


def load_settings_from_json(file_path: str = 'settings.json') -> MasterSettings:
    """
    Loads settings from a JSON file, using defaults for missing or invalid fields.
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return MasterSettings()

    return MasterSettings(
        Dakar=DakarSettings(**data.get('Dakar', {})),
        plotter=PlotterSettings(**data.get('DakarPlot', {}))
    )


def save_settings_to_json(settings: MasterSettings = None, file_path: str = r'Source code\json\default_settings.json') -> None:
    """Saves MasterSettings to a JSON file, using defaults if settings is None."""
    if settings is None:
        settings = MasterSettings()
    os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(asdict(settings), f, indent=4)
    print('Succesfully saved json')

save_settings_to_json()
