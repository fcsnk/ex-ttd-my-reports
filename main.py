import logging

from keboola.component.base import ComponentBase
from keboola.component import UserException

from ttd import TradeDesk


class Component(ComponentBase):

    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(__name__)

    def run(self):
        params = self.configuration.parameters
        self._logger.debug(f"Running component with following params: {params}")
        ttd_client = TradeDesk(username=params.get("username"), password=params.get("#password"))
        report_url = ttd_client.get_report_url(report_schedule_id=params.get("report_schedule_id"),
                                               advertiser_id=params.get("advertiser_id"))
        data = ttd_client.get_data(report_url)
        self._logger.info("Processing report.")
        is_incremental = bool(params.get("incremental_output"))

        table = self.create_out_table_definition("output.csv", incremental=is_incremental,
                                                 primary_key=params.get("primary_keys"))

        with open(table.full_path, mode="wt", encoding="utf-8", newline="") as out_file:
            out_file.write(data.text)

        self.write_manifest(table)


if __name__ == "__main__":
    try:
        comp = Component()
        comp.execute_action()
    except UserException as exc:
        logging.exception(exc)
        exit(1)
    except Exception as exc:
        logging.exception(exc)
        exit(2)
