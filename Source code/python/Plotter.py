import numpy as np
from matplotlib.lines import Line2D
from matplotlib import pyplot as plt
import cv2
from scipy.spatial import KDTree
from settings import PlotterSettings


class Plotter:
    """
    A plotting tool for Dakar data, configured upon initialization.
    It handles the business rule of mapping 'FM Size' to specific
    marker shapes as defined in its configuration.
    """
    def __init__(self, data, settings: PlotterSettings):
        """
        Initialize the DakarPlotter with data and settings.

        Args:
            data: The data to plot
            settings: PlotterSettings containing plot configuration
        """
        self.settings = settings
        self.background_image_path = self.settings.background_image_path
        self._base_legend_elements = self._build_base_legend()
        self.title = None
        self.data = self._assign_marker_category(data)

    def _assign_marker_category(self, data):
        """
        Assigns a marker category to each row based on 'FM Size'
        and the rules in the 'shape_mapping' config.
        """
        def get_category(fm_size):
            for category_name, details in self.settings.shape_mapping.items():
                # Skip 'other' until the end
                if category_name == 'other':
                    continue
                if details['min_size'] <= fm_size < details['max_size']:
                    return category_name
            # If no other category matched, return 'other'
            return 'other'

        # Create a new column with the assigned category for each point
        data['marker_category'] = data['FM SIZE'].apply(get_category)
        return data

    def _build_base_legend(self):
        legend_elements = [
            Line2D([0], [0], color=self.settings.points['top_color'], lw=4, label='Top'),
            Line2D([0], [0], color=self.settings.points['bottom_color'], lw=4, label='Bottom'),
            Line2D([0], [0], marker='', color='w', label='')  # Spacer
        ]

        # Dynamically create legend entries from the config
        for details in self.settings.shape_mapping.values():
            legend_elements.append(
                Line2D([0], [0], marker=details['marker'], color='grey',
                       label=details['label'], markersize=10, linestyle='None')
            )
        return legend_elements

    def _plot_points(self, ax, points_data, color):
        marker_size = self.settings.points['marker_size']
        shape_mapping = self.settings.shape_mapping
        default_marker = shape_mapping['other']['marker']

        # Group by the newly created 'marker_category' to use the correct marker
        for category_name, group in points_data.groupby('marker_category'):
            marker_style = shape_mapping.get(category_name, {}).get('marker', default_marker)
            ax.scatter(group['X PERCENTAGE'], group['Y PERCENTAGE'], s=marker_size,
                       marker=marker_style, c=color, zorder=10)

    def _generate_plot(self, title, data):
        """
        Categorizes data based on FM Size and generates a plot.
        """
        plot_data = data.copy()
        fig, ax = plt.subplots(figsize=self.settings.figure['figsize'])
        fig.subplots_adjust(left=self.settings.figure['margin_left'])

        img = plt.imread(self.background_image_path)
        ax.imshow(img, extent=[0, 1, 1, 0], aspect='auto', zorder=1)
        ax.set_title(title, fontweight='bold', fontsize=16)

        if not plot_data.empty:
            # Group by 'Top-Bottom' for coloring
            for group_name, group_data in plot_data.groupby('TOP BOTTOM'):
                if group_name == 'top':
                    color = self.settings.points['top_color']
                    self._plot_points(ax, group_data, color)
                elif group_name == 'bottom':
                    color = self.settings.points['bottom_color']
                    self._plot_points(ax, group_data, color)

        top_count = len(plot_data[plot_data['TOP BOTTOM'] == 'top'])
        bottom_count = len(plot_data[plot_data['TOP BOTTOM'] == 'bottom'])
        summary_text = (f"--- Summary ---\nTop Points:    {top_count}\n"
                        f"Bottom Points: {bottom_count}\nTotal Points:  {top_count + bottom_count}")

        legend_cfg = self.settings.legend
        ax.legend(handles=self._base_legend_elements,
                 loc=legend_cfg['location'],
                 bbox_to_anchor=legend_cfg['anchor'],
                 fontsize=legend_cfg['fontsize'],
                 title=legend_cfg['title'],
                 title_fontsize=legend_cfg['title_fontsize'])

        summary_cfg = self.settings.summary_text
        ax.text(*summary_cfg['location'], summary_text,
                transform=ax.transAxes,
                fontsize=summary_cfg['fontsize'],
                verticalalignment='top',
                horizontalalignment='left', bbox=summary_cfg['box_props'])

        ax.axis('off')
        fig.canvas.draw()
        rgba_array = np.array(fig.canvas.renderer.buffer_rgba())
        bgr_array = cv2.cvtColor(rgba_array, cv2.COLOR_RGBA2BGR)
        plt.close(fig)
        return bgr_array, title, top_count, bottom_count

    def _compare_states(self, name_filter, state_before, state_after, tolerance=0.02):
        """
        Compares two states using a spatial tolerance for x/y coordinates.
        Returns the added, removed, and stayed points as three separate DataFrames.
        """
        names_to_filter = name_filter if isinstance(name_filter, list) else [name_filter]
        data_before = self.data[(self.data['NAME'].isin(names_to_filter)) & (self.data['STATE'] == state_before)].copy()
        data_after = self.data[(self.data['NAME'].isin(names_to_filter)) & (self.data['STATE'] == state_after)].copy()
        exact_match_keys = ['NAME', 'TOP BOTTOM']
        matched_before_indices = set()
        matched_after_indices = set()
        grouped_before = data_before.groupby(exact_match_keys)
        grouped_after = data_after.groupby(exact_match_keys)

        for group_keys, after_group in grouped_after:
            if group_keys not in grouped_before.groups:
                continue
            before_group = grouped_before.get_group(group_keys)
            if before_group.empty or after_group.empty:
                continue
            coords_before = before_group[['X PERCENTAGE', 'Y PERCENTAGE']].values
            coords_after = after_group[['X PERCENTAGE', 'Y PERCENTAGE']].values
            kdtree = KDTree(coords_before)
            distances, closest_indices = kdtree.query(coords_after, k=1)
            used_before_indices = set()
            for i, (dist, closest_idx) in enumerate(zip(distances, closest_indices)):
                if dist <= tolerance and closest_idx not in used_before_indices:
                    matched_after_indices.add(after_group.index[i])
                    matched_before_indices.add(before_group.index[closest_idx])
                    used_before_indices.add(closest_idx)

        removed_indices = set(data_before.index) - matched_before_indices
        removed_points = data_before.loc[list(removed_indices)]
        added_indices = set(data_after.index) - matched_after_indices
        added_points = data_after.loc[list(added_indices)]
        stay_points = data_after.loc[list(matched_after_indices)]
        return added_points, removed_points, stay_points

    def create_FM_position_plot(self, name_filter, state_filter, top_bottom_filter):
        """
        Filters data based on all criteria and tells the plotter to generate an image.
        The name_filter can be a single string or a list of strings.
        """
        # Prepare the name filter to handle both string and list inputs
        names_to_filter = name_filter
        if isinstance(name_filter, str):
            names_to_filter = [name_filter]

        # A single, powerful filter that includes all criteria
        filtered_data = self.data[
            (self.data['NAME'].isin(names_to_filter)) &
            (self.data['STATE'] == state_filter) &
            (self.data['TOP BOTTOM'].isin(top_bottom_filter))
        ]

        plot_title = f"Name(s): {names_to_filter} | State: {state_filter}"

        return self._generate_plot(plot_title, filtered_data)

    def create_FM_change_plots(self, name_filter, state_before, state_after):
        """
        Generates plots for added, removed, and stayed points using a
        more concise, loop-based approach.
        """
        added_points, removed_points, stay_points = self._compare_states(name_filter, state_before, state_after)
        plot_data_map = {"Added": added_points, "Removed": removed_points, "Stayed": stay_points}

        plots = []
        for plot_type, data_to_plot in plot_data_map.items():
            title = f"{plot_type} FM for {name_filter} from {state_before} to {state_after}"
            plot_image, title, top, bottom = self._generate_plot(
                title=title,
                data=data_to_plot
            )
            plots.append((plot_image, title, top, bottom))
        return plots

    def create_summary_plot(self, before, after, added, removed, stayed, name, state1, state2):
        """
        Generates a single summary image with a text report and a refined 3-bar chart.
        The bar width is controlled, and the stacked bar has individual labels.
        The final image dimensions match the input plot images.
        """
        # --- Step 1: Unpack all the data and calculate totals ---
        before_image, _, before_top_count, before_bottom_count = before
        _, _, after_top_count, after_bottom_count = after
        _, _, add_top_count, add_bottom_count = added
        _, _, removed_top_count, removed_bottom_count = removed
        _, _, stay_top_count, stay_bottom_count = stayed

        before_total = before_top_count + before_bottom_count
        after_total = after_top_count + after_bottom_count
        add_total = add_top_count + add_bottom_count
        removed_total = removed_top_count + removed_bottom_count
        stay_total = stay_top_count + stay_bottom_count

        # --- Step 2: Create the main figure canvas ---
        height, width, _ = before_image.shape
        dpi = 100
        fig, ax = plt.subplots(figsize=(width / dpi, height / dpi), dpi=dpi)
        fig.patch.set_facecolor('white')
        ax.axis('off')

        # --- Step 3: Place the formatted text on the TOP half ---
        report_text = (
            f"Analysis Report for: {name}\n"
            f"Transition: {state1} -> {state2}\n"
            f"---------------------------------------------------\n"
            f"Before:  Top: {before_top_count:>4} | Bottom: {before_bottom_count:>4} | Total: {before_total:>4}\n"
            f"After:   Top: {after_top_count:>4} | Bottom: {after_bottom_count:>4} | Total: {after_total:>4}\n"
            f"---------------------------------------------------\n"
            f"Stayed:  Top: {stay_top_count:>4} | Bottom: {stay_bottom_count:>4} | Total: {stay_total:>4}\n"
            f"Removed: Top: {removed_top_count:>4} | Bottom: {removed_bottom_count:>4} | Total: {removed_total:>4}\n"
            f"Added:   Top: {add_top_count:>4} | Bottom: {add_bottom_count:>4} | Total: {add_total:>4}\n"
        )
        fig.text(0.5, 0.73, report_text, ha='center', va='center', fontsize=16, fontfamily='monospace')

        # --- Step 4: Create a NEW axes on the BOTTOM half for the bar chart ---
        ax_chart = fig.add_axes([0.1, 0.1, 0.8, 0.35])

        # --- Step 5: Draw the 3-bar chart with refined aesthetics ---
        bar_width = 0.2  # Control the width of the bars for a sleeker look

        # Plot the simple 'Before' and 'After' bars
        ax_chart.bar('Before', before_total, width=bar_width, color='#1f77b4')

        # --- NEW: Logic for STACKED bar with individual labels ---
        stacked_data = [stay_total, removed_total, add_total]
        stacked_labels = ['Stayed', 'Removed', 'Added']
        stacked_colors = ['#2ca02c', '#d62728', '#9467bd']  # Green, Red, Purple

        bottom_offset = 0
        for i, count in enumerate(stacked_data):
            # Draw the bar segment
            ax_chart.bar('Changes', count, width=bar_width, bottom=bottom_offset,
                         color=stacked_colors[i], label=stacked_labels[i])

            # Add text label in the middle of the segment, but only if the count is > 0
            if count > 0:
                y_center = bottom_offset + count / 2
                ax_chart.text('Changes', y_center, str(count), ha='center', va='center',
                              color='white', fontsize=12, fontweight='bold')

            # Update the bottom offset for the next segment
            bottom_offset += count

        ax_chart.bar('After', after_total, width=bar_width, color='#1f77b4')

        # Add text labels on top of the simple bars
        ax_chart.text('Before', before_total, f'{before_total}', ha='center', va='bottom', fontsize=12,
                      fontweight='bold', bbox=dict(facecolor='white', alpha=0.5, edgecolor='none',
                                                   boxstyle='round,pad=0.2'))
        ax_chart.text('After', after_total, f'{after_total}', ha='center', va='bottom', fontsize=12,
                      fontweight='bold', bbox=dict(facecolor='white', alpha=0.5, edgecolor='none',
                                                   boxstyle='round,pad=0.2'))

        # --- Chart Customization ---
        ax_chart.set_ylabel('Total Counts', fontsize=12)
        ax_chart.set_title('Summary of Changes', fontsize=16, fontweight='bold')
        ax_chart.tick_params(axis='x', labelsize=12)
        ax_chart.legend(loc='upper right')
        ax_chart.grid(axis='y', linestyle='--', alpha=0.6)

        # Add a top margin to make space for the bar labels
        ax_chart.margins(y=0.15)

        # --- Step 6: Convert the entire figure to a CV2 image ---
        fig.canvas.draw()
        rgba_array = np.array(fig.canvas.renderer.buffer_rgba())
        bgr_array = cv2.cvtColor(rgba_array, cv2.COLOR_RGBA2BGR)
        plt.close(fig)

        return bgr_array
