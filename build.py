import os
import shutil
from distutils.core import Distribution
from pathlib import Path
from subprocess import call

from setuptools_rust import Binding, RustExtension, build_rust


# class BuildFailed(Exception):
#     pass


def build(setup_kwargs):
    """
    This function is mandatory in order to build the extensions.
    """

    print("setup_kwargs:", setup_kwargs)

    print("os.curdir:", os.getcwd())
    original_project_dir = os.path.dirname(os.path.realpath(__file__))
    cargo_toml_path = os.path.join("defi-wallet-core-rs", "common", "Cargo.toml")
    print("original_project_dir:", original_project_dir)
    print("cargo_toml_path:", cargo_toml_path)
    print(os.listdir())
    target_name = "chainlibpy.generated.defi_wallet_core_common"
    extension = RustExtension(
        target=target_name,
        path=cargo_toml_path,
        features=["uniffi-binding"],
        binding=Binding.NoBinding,
    )
    print(extension)
    lib_name = extension.get_lib_name(quiet=False)
    print("lib_name:", lib_name)

    # https://docs.python.org/3/distutils/apiref.html#distutils.core.Distribution
    dist = Distribution(attrs=setup_kwargs)

    builder = build_rust(dist)
    builder.initialize_options()
    builder.finalize_options()
    dpaths = builder.build_extension(extension)
    builder.install_extension(extension, dylib_paths=dpaths)
    print("Extension built!")
    print("*********** 0.")
    call(["find", "."])
    print("*********** 1.")
    p = Path(builder.get_dylib_ext_path(extension, target_name))
    np = Path(p.parent, "{}{}".format("libdefi_wallet_core_common", p.suffix))
    p.rename(np)
    shutil.copyfile(
        np, os.path.join("chainlibpy", "generated", "libdefi_wallet_core_common" + p.suffix)
    )
    print("dylib path:", p)

    # raise BuildFailed("Just to see the logs")
