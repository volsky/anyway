from typing import Dict, List

from flask_babel import _

from anyway.backend_constants import InjurySeverity, BE_CONST as BE
from anyway.request_params import RequestParams
from anyway.widgets.suburban_widgets.killed_and_injured_count_per_age_group_widget_utils import (
    KilledAndInjuredCountPerAgeGroupWidgetUtils,
    AGE_RANGES,
)
from anyway.widgets.suburban_widgets import killed_and_injured_count_per_age_group_widget_utils

from anyway.widgets.suburban_widgets.sub_urban_widget import SubUrbanWidget
from anyway.widgets.widget import register
from anyway.widgets.widget_utils import add_empty_keys_to_gen_two_level_dict, gen_entity_labels

INJURY_ORDER = [InjurySeverity.LIGHT_INJURED, InjurySeverity.SEVERE_INJURED, InjurySeverity.KILLED]


@register
class KilledInjuredCountPerAgeGroupStackedWidget(SubUrbanWidget):
    name: str = "killed_and_injured_count_per_age_group_stacked"
    files = [__file__, killed_and_injured_count_per_age_group_widget_utils.__file__]

    def __init__(self, request_params: RequestParams):
        super().__init__(request_params)
        self.rank = 30

    def generate_items(self) -> None:
        raw_data = KilledAndInjuredCountPerAgeGroupWidgetUtils.filter_and_group_injured_count_per_age_group(
            self.request_params
        )

        partial_processed = add_empty_keys_to_gen_two_level_dict(
            raw_data, self.get_age_range_list(), InjurySeverity.codes()
        )

        structured_data_list = []
        for age_group, severity_dict in partial_processed.items():
            ordered_list = [
                {BE.LKEY: inj.get_label(), BE.VAL: severity_dict.get(inj.value, 0)}
                for inj in INJURY_ORDER
            ]
            structured_data_list.append({BE.LKEY: age_group, BE.SERIES: ordered_list})

        self.items = structured_data_list

    @staticmethod
    def localize_items(request_params: RequestParams, items: Dict) -> Dict:
        items["data"]["text"] = {
            "title": _("Killed and injury stacked per age group"),
            "subtitle": _("In") + " " + request_params.location_info["road_segment_name"],
            "labels_map": gen_entity_labels(InjurySeverity),
        }
        return items

    @staticmethod
    def get_age_range_list() -> List[str]:
        return [f"{item_min_range}-{item_max_range}" if item_max_range < 120 else f"{item_min_range}+"
                for item_min_range, item_max_range in zip(AGE_RANGES, AGE_RANGES[1:])]
