from dataclasses import dataclass, field,asdict
from typing import Dict, Any,List
import os 
import json


@dataclass
class Run_Excel:

    input_file: str = field(
        default=r'CSV\AfterFoilDetach_AfterLaserCut_TESTING.xlsx',
        metadata={"tooltip": "Path"}
    )

    output_file: str = field(
        default=r'CSV\AfterFoilDetach_AfterLaserCut_TESTING.xlsx',
        metadata={"tooltip": "Path "}
    )


@dataclass
class plot_complete_FM_summary_settings:

    output_folder: str = field(
        default=r'Result\SummaryPlot\V3',
        metadata={"tooltip": "Path to the folder containing complete FM summary files"}
    )

   #states_to_compare: List = field(
   #    default=["AfterFoilDetach","AfterLaserCut"],
   #    metadata={"tooltip": "List of state to compare for plot summary"}
   #)

@dataclass
class crop_FM_classify_top_bottom_Settings:
    raw_image_input_folder: str = field(
        #default=r'data\IncomingState',
        default=r'data',

        metadata={"tooltip": "Path to the folder containing raw images for processing"}
    )

    image_output_folder: str = field(
        default=r'Result\crop_to_classify_top_bottom\incomingstate\v1',
        metadata={"tooltip": "Path to the folder containing cropped and combined images"}
    )
    min_fm_size: int = field(
        default=100,
        metadata={"tooltip": "Minimum FM size to filter"}
    )
    max_fm_size: int = field(
        default=700,
        metadata={"tooltip": "Maximum FM size to filter"}
    )

@dataclass
class crop_FM_check_background_fm_settings:
    raw_image_input_folder: str = field(
        default=r'data\IncomingState\incomingfoil2',
        metadata={"tooltip": "Path to the folder containing raw images for processing"}
    )

    image_output_folder: str = field(
        default=r'Result\Crop_to_classify_background\incomingstate',
        metadata={"tooltip": "Path to the folder containing cropped and combined images"}
    )

    min_fm_size: int = field(
        default=100,
        metadata={"tooltip": "Minimum FM size to filter"}
    )
    max_fm_size: int = field(
        default=2000,
        metadata={"tooltip": "Maximum FM size to filter"}
    )



@dataclass
class DakarSettings:

    Excel_input_path: str = field(
        default=r'CSV\ManualDetach Gap Analysis.xlsx',
        metadata={"tooltip": "Path to the Excel file for Dakar data"}

    )

    Excel_copy_path: str = field(
        default=r'CSV\ManualDetach Gap Analysis_copy.xlsx',
        metadata={"tooltip": "Path to the Excel file for Dakar data"}

    )



    worksheet_to_read: str = field(
        #default='incomingfoil1',
        default='copy data',

        metadata={"tooltip": "The name of the worksheet to read"}

    )

    image_width: str = field(
        default=66320,
        metadata={"tooltip": "The width of image"}
    )
    image_height: str = field(
        default=55080,
        metadata={"tooltip": "The height of image"}
    )


    crop_FM_classify_top_bottom :crop_FM_classify_top_bottom_Settings = field(
        default_factory=crop_FM_classify_top_bottom_Settings
    )

    crop_FM_check_background_fm:crop_FM_check_background_fm_settings = field(
        default_factory=crop_FM_check_background_fm_settings
    )

    plot_complete_FM_summary :plot_complete_FM_summary_settings = field(
        default_factory=plot_complete_FM_summary_settings
    )

    run_excel :Run_Excel = field(
        default_factory=Run_Excel
    )
    

@dataclass
class PlotterSettings:
    background_image_path: str = field(
        default='data/original_resize.jpg',
        metadata={"tooltip": "Path to the background image for plots"}
    )
    figure: Dict[str, Any] = field(
        default_factory=lambda: {
            "figsize": [17, 12],
            "margin_left": 0.15
        },
        metadata={"tooltip": "Figure settings (e.g., size, margins)"}
    )
    legend: Dict[str, Any] = field(
        default_factory=lambda: {
            "location": "upper left",
            "anchor": [-0.15, 1.0],
            "fontsize": 12,
            "title": "Legend",
            "title_fontsize": 14
        },
        metadata={"tooltip": "Legend settings (e.g., location, font size)"}
    )
    points: Dict[str, Any] = field(
        default_factory=lambda: {
            "marker_size": 80.0,
            "bottom_color": "blue",
            "top_color": "red"
        },
        metadata={"tooltip": "Point settings (e.g., marker size, colors)"}
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
        metadata={"tooltip": "Mapping of shapes to plot properties"}
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
        metadata={"tooltip": "Summary text settings (e.g., location, font size)"}
    )

@dataclass
class MasterSettings:
    Dakar: DakarSettings = field(
        default_factory=DakarSettings
    )
    plotter: PlotterSettings = field(
        default_factory=PlotterSettings
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

save_settings_to_json()