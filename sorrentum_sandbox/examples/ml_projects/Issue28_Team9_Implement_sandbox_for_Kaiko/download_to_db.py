# kaiko


import argparse
import logging

import pandas as pd

import helpers.hdbg as hdbg
import helpers.hparser as hparser
import Issue28_Team9_Implement_sandbox_for_Kaiko.db_kaiko as sisebidb
import Issue28_Team9_Implement_sandbox_for_Kaiko.download_kaiko as sisebido

_LOG = logging.getLogger(__name__)


def _add_download_args(
    parser: argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    """
    Add the command line options for exchange download.
    """
    parser.add_argument(
        "--start_timestamp",
        required=True,
        action="store",
        type=str,
        help="Beginning of the loaded period, e.g. 2022-02-09 10:00:00+00:00",
    )
    parser.add_argument(
        "--end_timestamp",
        action="store",
        required=True,
        type=str,
        help="End of the loaded period, e.g. 2022-02-10 10:00:00+00:00",
    )
    parser.add_argument(
        "--target_table",
        action="store",
        required=True,
        type=str,
        help="Name of the db table to save data into",
    )
    parser.add_argument(
        "--use_global_api",
        action="store_true",
        required=False,
        default=False,
        help="Domain switcher between binance.com when using --use_global_api"
             " and binance.us by default"
    )
    return parser


def _parse() -> argparse.ArgumentParser:
    hdbg.init_logger(use_exec_path=True)
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser = _add_download_args(parser)
    parser = hparser.add_verbosity_arg(parser)
    return parser


def _main(parser: argparse.ArgumentParser) -> None:
    args = parser.parse_args()
    # Load data.
    start_timestamp = pd.Timestamp(args.start_timestamp)
    end_timestamp = pd.Timestamp(args.end_timestamp)
    downloader = sisebido.OhlcvRestApiDownloader(args.use_global_api)
    raw_data = downloader.download(start_timestamp, end_timestamp)
    # Save data to DB.
    db_conn = sisebidb.get_db_connection()
    saver = sisebidb.PostgresDataFrameSaver(db_conn)
    saver.save(raw_data, args.target_table)


if __name__ == "__main__":
    _main(_parse())