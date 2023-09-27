import functools
import sui_brownie
from pathlib import Path
from typing import Union

PROJECT_PATH = Path(__file__).parent.parent
sui_project = sui_brownie.SuiProject(
    project_path=PROJECT_PATH,
    network="sui-testnet"
)

@functools.lru_cache()
def get_upgrade_cap_info(upgrade_cap_ids: tuple):
    result = sui_project.client.sui_multiGetObjects(
        upgrade_cap_ids,
        {
            "showType": True,
            "showOwner": True,
            "showPreviousTransaction": False,
            "showDisplay": False,
            "showContent": True,
            "showBcs": False,
            "showStorageRebate": False
        }
    )
    return {v["data"]["content"]["fields"]["package"]: v["data"] for v in result if "error" not in v}


def get_upgrade_cap_ids():
    return list(tuple(list(sui_project["0x2::package::UpgradeCap"])))


def get_upgrade_cap_by_package_id(package_id: str):
    upgrade_cap_ids = tuple(list(sui_project["0x2::package::UpgradeCap"]))
    info = get_upgrade_cap_info(upgrade_cap_ids)
    if package_id in info:
        return info[package_id]["objectId"]

@functools.lru_cache()
def sui_package(package_id: str = None, package_path: Union[Path, str] = None):
    return sui_brownie.SuiPackage(
        package_id=package_id,
        package_path=package_path
    )

def example_coins_package(package_id):
    return sui_package(package_id, PROJECT_PATH.joinpath("example_coins"))

def hello_token_package(package_id):
    return sui_package(package_id, PROJECT_PATH.joinpath("hello_token"))

def token_bridge_package(package_id):
    return sui_package(package_id,PROJECT_PATH.joinpath("token_bridge"))

def wormhole_package(package_id):
    return sui_package(package_id,PROJECT_PATH.joinpath("wormhole"))