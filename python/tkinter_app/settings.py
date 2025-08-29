from dataclasses import dataclass, field
from typing import Dict, Any,List


@dataclass
class DakarSettings:
    
    data: str = field(
        default=r'data',
        metadata={
            "tooltip": "Folder path containing all the necceasry images and csv files needed for analysis",
            "setting_type": "folder",
            "label": "",
            "layout_group": "row3_left",
            "widget_style": "icon_only"
        }
    )

    analysis_name: str = field(
        default=r'Gap Analysis',
        metadata={
            "tooltip": "The analysis name", 
            "label": "Analysis name",
            "layout_group": "row1"
        }
    )

    save_folder: str = field(
        default=r'result',
        metadata={
            "tooltip": "Folder for all  the combined images, and plotted summary of analysis", 
            "setting_type": "folder",
            "label": "Result folder",
            "layout_group": "row1"
        }
    )

    min_fm_size: int = field(
        default=100,
        metadata={"tooltip": "Minimum FM size to filter", "label": "Min FM Size", "layout_group": "row1"}
    )
    max_fm_size: int = field(
        default=700,
        metadata={"tooltip": "Maximum FM size to filter", "label": "Max FM Size", "layout_group": "row1"}
    )

    image_width: str = field(
        default=66320,
        metadata={"tooltip": "The width of image", "label": "Image Width", "layout_group": "row2", "visible_in_ui": False}
    )
    image_height: str = field(
        default=55080,
        metadata={"tooltip": "The height of image", "label": "Image Height", "layout_group": "row2", "visible_in_ui": False}
    )

    foils_to_plot : Dict =  field(
        default_factory=dict,
        metadata={"label": "Foils to Plot", "widget_type": "foils_selector", "layout_group": "row3_left"}
    )

    states_to_compare : Dict =  field(
        default_factory=dict,
        metadata={"label": "State to compare", "widget_type": "state_selector", "layout_group": "row3_right"}
    )




@dataclass
class PlotterSettings:
    background_image_path: str = field(
        default='background.jpg',
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