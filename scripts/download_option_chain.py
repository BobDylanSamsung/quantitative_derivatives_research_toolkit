from pathlib import Path

from derivative_pricing.calibration.option_chain import (
    download_option_chain,
    save_snapshot,
)


def main() -> None:
    quotes, metadata = download_option_chain("SPY")

    save_snapshot(
        quotes=quotes,
        metadata=metadata,
        output_directory=Path("data/raw/options"),
    )


if __name__ == "__main__":
    main()
